#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para coleta de registros de ponto do REP EVO
Baseado no TESTE.py fornecido
Coleta registros e salva em formato AFD671
"""

import socket
import base64
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.Util.Padding import pad, unpad
import struct
import time
from datetime import datetime

# employee_info_fields = dict(
#     8531537959=dict(
#         name
#     )
# )
class RepEvoCollector:
    def __init__(self, host='192.168.90.97', port=3000):
        self.host = host
        self.port = port
        self.socket = None
        self.aes_key = None
        self.rsa_public_key = None
        self.authenticated = False
        
    def connect(self):
        """Estabelece conexão TCP com o equipamento"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            print(f"Conectado ao REP EVO em {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def disconnect(self):
        """Fecha a conexão"""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.authenticated = False
            print("Desconectado do REP EVO")
    
    def calculate_checksum(self, data):
        """Calcula checksum XOR dos dados"""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum & 0xFF
    
    def send_basic_command(self, command_str):
        """Envia comando básico (não criptografado) no formato STX+LEN+DATA+CS+ETX"""
        print(f"Enviando comando básico: {command_str}")
        
        command_bytes = command_str.encode('ascii')
        
        packet = bytearray()
        packet.append(0x02)  # STX
        
        packet_len = len(command_bytes)
        packet.append(packet_len & 0xFF)  # Low byte
        packet.append((packet_len >> 8) & 0xFF)  # High byte
        
        packet.extend(command_bytes)  # Data
        
        checksum = self.calculate_checksum(packet[1:])
        packet.append(checksum)
        
        packet.append(0x03)  # ETX
        
        print(f"Enviando: {packet.hex()}")
        self.socket.send(packet)
    
    def send_encrypted_command(self, command_str):
        """Envia comando criptografado no formato STX+LEN+IV+DADOS_CRIPTOGRAFADOS+CS+ETX"""
        if not self.authenticated or not self.aes_key:
            raise Exception("Não autenticado ou chave AES não disponível")
        
        print(f"Enviando comando criptografado: {command_str}")
        
        iv = os.urandom(16)
        encrypted_data = self.encrypt_aes_manual_padding(command_str.encode('ascii'), iv)
        
        data_packet = iv + encrypted_data
        
        packet = bytearray()
        packet.append(0x02)  # STX
        
        packet_len = len(data_packet)
        packet.append(packet_len & 0xFF)  # Low byte
        packet.append((packet_len >> 8) & 0xFF)  # High byte
        
        packet.extend(data_packet)  # IV + dados criptografados
        
        checksum = self.calculate_checksum(packet[1:])
        packet.append(checksum)
        
        packet.append(0x03)  # ETX
        
        print(f"Enviando: {packet.hex()}")
        self.socket.send(packet)
    
    def receive_response(self, timeout=30):
        """Recebe resposta do equipamento com timeout maior para registros"""
        self.socket.settimeout(timeout)
        
        try:
            # Recebe STX
            stx = self.socket.recv(1)
            if not stx or stx[0] != 0x02:
                raise Exception(f"STX inválido: {stx.hex() if stx else 'vazio'}")
            
            # Recebe tamanho (2 bytes, little endian)
            len_bytes = self.socket.recv(2)
            if len(len_bytes) < 2:
                raise Exception("Não recebeu bytes de tamanho completos")
            
            packet_len = len_bytes[0] | (len_bytes[1] << 8)  # Little endian
            print(f"Tamanho do pacote: {packet_len}")
            
            # Recebe dados
            data = b''
            while len(data) < packet_len:
                chunk = self.socket.recv(min(4096, packet_len - len(data)))
                if not chunk:
                    break
                data += chunk
            
            # Recebe checksum e ETX
            cs_etx = self.socket.recv(2)
            if len(cs_etx) < 2:
                raise Exception("Não recebeu checksum e ETX completos")
            
            checksum = cs_etx[0]
            etx = cs_etx[1]
            
            if etx != 0x03:
                raise Exception(f"ETX inválido: {etx:02x}")
            
            # Verifica checksum
            expected_cs = self.calculate_checksum(len_bytes + data)
            if checksum != expected_cs:
                print(f"AVISO: Checksum inválido: esperado {expected_cs:02x}, recebido {checksum:02x}")
            
            full_packet = stx + len_bytes + data + cs_etx
            print(f"Recebido: {len(full_packet)} bytes")
            
            return data
            
        except Exception as e:
            print(f"Erro ao receber resposta: {e}")
            raise
    
    def encrypt_aes_manual_padding(self, data, iv):
        """Criptografia AES com padding manual (como no código C#)"""
        padded_data = bytearray(data)
        while len(padded_data) % 16 != 0:
            padded_data.append(0x00)
        
        cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(bytes(padded_data))
        
        return encrypted
    
    def decrypt_aes(self, data, iv):
        """Descriptografa dados com AES CBC"""
        cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(data)
        
        return decrypted.rstrip(b'\x00')
    
    def parse_basic_response(self, response_data):
        """Processa resposta de comando básico"""
        response_str = response_data.decode('ascii', errors='ignore')
        clean_response = ''.join(c for c in response_str if ord(c) >= 32 or c in '\r\n\t')
        clean_response = clean_response.strip()
        
        print(f"Resposta limpa: {clean_response}")
        return clean_response
    
    def parse_encrypted_response(self, response_data):
        """Processa resposta de comando criptografado"""
        if len(response_data) < 16:
            raise Exception("Resposta muito pequena para conter IV")
        
        iv = response_data[:16]
        encrypted_data = response_data[16:]
        
        decrypted = self.decrypt_aes(encrypted_data, iv)
        response_str = decrypted.decode('ascii', errors='ignore')
        
        print(f"Resposta descriptografada (primeiros 200 chars): {response_str[:200]}...")
        return response_str
    
    def request_public_key(self):
        """Solicita chave pública RSA (comando 1+RA+00)"""
        print("Solicitando chave pública RSA...")
        
        self.send_basic_command("1+RA+00")
        response_data = self.receive_response()
        
        try:
            response_str = self.parse_basic_response(response_data)
            
            print(f"Resposta completa: {response_str}")
            
            if "+000+" in response_str:
                key_data = response_str.split("+000+", 1)[1]
                
                print(f"Dados da chave: {key_data[:100]}...")
                
                if ']' in key_data:
                    modulus_b64, exponent_b64 = key_data.split(']', 1)
                    
                    modulus_b64 = modulus_b64.strip()
                    exponent_b64 = exponent_b64.strip()
                    
                    print(f"Modulus (base64): {modulus_b64[:50]}...")
                    print(f"Exponent (base64): {exponent_b64}")
                    
                    modulus_bytes = base64.b64decode(modulus_b64)
                    exponent_bytes = base64.b64decode(exponent_b64)
                    
                    modulus = int.from_bytes(modulus_bytes, byteorder='big')
                    exponent = int.from_bytes(exponent_bytes, byteorder='big')
                    
                    self.rsa_public_key = RSA.construct((modulus, exponent))
                    print(f"Chave RSA criada: {modulus.bit_length()} bits")
                    return True
                else:
                    print("Não encontrou ']' separando modulus e exponent")
            else:
                print("Não encontrou '+000+' na resposta")
            
            print("Formato de resposta inesperado")
            return False
            
        except Exception as e:
            print(f"Erro ao processar chave pública: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def authenticate(self, username="teste fabrica", password="111111"):
        """Realiza autenticação (comando 2+EA+00+...)"""
        if not self.rsa_public_key:
            print("Chave pública RSA não disponível")
            return False
        
        print(f"Autenticando usuário: {username}")
        
        self.aes_key = os.urandom(16)
        aes_key_b64 = base64.b64encode(self.aes_key).decode('ascii')
        
        auth_packet = f"1]{username}]{password}]{aes_key_b64}"
        print(f"Pacote de autenticação: {auth_packet}")
        
        cipher_rsa = PKCS1_v1_5.new(self.rsa_public_key)
        encrypted_data = cipher_rsa.encrypt(auth_packet.encode('ascii'))
        
        encrypted_b64 = base64.b64encode(encrypted_data).decode('ascii')
        
        ea_command = f"2+EA+00+{encrypted_b64}"
        self.send_basic_command(ea_command)
        
        try:
            response_data = self.receive_response()
            response_str = self.parse_basic_response(response_data)
            
            print(f"Resposta da autenticação: {response_str}")
            
            if "000" in response_str:
                self.authenticated = True
                print("Autenticação realizada com sucesso!")
                return True
            else:
                print("Falha na autenticação")
                return False
                
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return False

    def get_employer_info(self):
        """Obtém informações do empregador (comando RE)"""
        if not self.authenticated:
            print("Não autenticado")
            return None
        
        print("Solicitando informações do empregador...")
        command = "01+RE+00"
        
        self.send_encrypted_command(command)
        
        try:
            response_data = self.receive_response()
            response_str = self.parse_encrypted_response(response_data)
            return response_str
        except Exception as e:
            print(f"Erro ao obter informações do empregador: {e}")
            return None

    def get_rep_info(self):
        """Obtém informações do REP (comando RC para algumas configurações)"""
        if not self.authenticated:
            print("Não autenticado")
            return None
        
        print("Solicitando informações do REP...")
        # Solicita informações específicas necessárias para o cabeçalho
        command = "01+RC+00+NR_REP]MODELO]VERSAO_PRODUTO]CHAVE_PUBLICA"
        
        self.send_encrypted_command(command)
        
        try:
            response_data = self.receive_response()
            response_str = self.parse_encrypted_response(response_data)
            return response_str
        except Exception as e:
            print(f"Erro ao obter informações do REP: {e}")
            return None

    def get_rep_datetime(self):
        """Obtém número de série do REP (comando RB)"""
        if not self.authenticated:
            print("Não autenticado")
            return None
        
        print("Solicitando data e hora do REP...")
        command = "01+RH+00"
        
        self.send_encrypted_command(command)
        
        try:
            response_data = self.receive_response()
            response_str = self.parse_encrypted_response(response_data)
            return response_str
        except Exception as e:
            print(f"Erro ao obter data e hora do equipamento: {e}")
            return None
    
    def get_registers_by_memory(self, start_address=0, quantity=214748364):
        """
        Coleta registros por endereço de memória (comando RR com parâmetro M)
        start_address: Endereço inicial (padrão 0)
        quantity: Quantidade de registros (padrão: máximo)
        """
        if not self.authenticated:
            print("Não autenticado")
            return None
        
        print(f"Coletando registros por memória - Endereço: {start_address}, Quantidade: {quantity}")
        command = f"06+RR+00+M]{start_address}]{quantity}"
        
        self.send_encrypted_command(command)
        
        try:
            response_data = self.receive_response(timeout=60)  # Timeout maior para muitos registros
            response_str = self.parse_encrypted_response(response_data)
            
            return response_str
            
        except Exception as e:
            print(f"Erro ao coletar registros por memória: {e}")
            return None
    
    def get_registers_by_nsr(self, start_nsr=1, quantity=100):
        """
        Coleta registros por NSR (comando RR com parâmetro N)
        start_nsr: NSR inicial (padrão 1)  
        quantity: Quantidade de registros (padrão: máximo)
        """
        if not self.authenticated:
            print("Não autenticado")
            return None
        
        print(f"Coletando registros por NSR - NSR inicial: {start_nsr}, Quantidade: {quantity}")
        command = f"07+RR+00+N]{quantity}]{start_nsr}"
        
        self.send_encrypted_command(command)
        
        try:
            response_data = self.receive_response(timeout=60)
            response_str = self.parse_encrypted_response(response_data)
            
            return response_str
            
        except Exception as e:
            print(f"Erro ao coletar registros por NSR: {e}")
            return None
    
    def get_registers_by_date(self, start_date="01/01/2010 12:00:01", quantity=2):
        """
        Coleta registros por data (comando RR com parâmetro D)
        start_date: Data inicial no formato dd/mm/yyyy hh:mm:ss
        quantity: Quantidade de registros
        """
        if not self.authenticated:
            print("Não autenticado")
            return None

        print(f"Coletando registros por data - Data inicial: {start_date}, Quantidade: {quantity}")
        # Comando conforme solicitado: 01+RR+00+D]2]10/07/2012 08:00:01]
        command = f"01+RR+00+D]{quantity}]{start_date}]"

        self.send_encrypted_command(command)

        try:
            response_data = self.receive_response(timeout=60)
            response_str = self.parse_encrypted_response(response_data)
            return response_str
        except Exception as e:
            print(f"Erro ao coletar registros por data: {e}")
            return None
    
    def save_to_afd(self, data, filename=None):
        """Salva os dados em arquivo AFD671"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"registros_rep_evo_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(data)
            
            print(f"Registros salvos em: {filename}")
            print(f"Tamanho do arquivo: {len(data)} caracteres")
            return filename
            
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            return None
    
    def collect_all_registers(self, method="nsr", save_file=True):
        """
        Coleta todos os registros do equipamento
        method: "nsr", "memory" ou "date"
        save_file: Se True, salva automaticamente em arquivo
        """
        print(f"\n=== COLETANDO REGISTROS POR {method.upper()} ===")
        
        registers_data = None
        
        if method == "nsr":
            registers_data = self.get_registers_by_nsr()
        elif method == "memory":
            registers_data = self.get_registers_by_memory()
        elif method == "date":
            registers_data = self.get_registers_by_date()
        else:
            print("Método inválido. Use: nsr, memory ou date")
            return None
        
        if registers_data:
            print(f"\nRegistros coletados com sucesso!")
            print(f"Tamanho dos dados: {len(registers_data)} caracteres")
            print(f"Primeiros 500 caracteres:\n{registers_data[:500]}")
            print("...")
            print(f"Últimos 200 caracteres:\n{registers_data[-200:]}")
            
            if save_file:
                filename = self.save_to_afd(registers_data)
                return filename, registers_data
            
            return registers_data
        else:
            print("Falha ao coletar registros")
            return None

def main():
    """Função principal"""
    print("=== COLETOR DE REGISTROS REP EVO ===\n")
    
    # Configurações
    host = "192.168.1.11"
    port = 3000
    username = "teste fabrica"
    password = "132435"
    
    collector = RepEvoCollector(host=host, port=port)
    
    try:
        # Conecta
        print("1. Conectando ao equipamento...")
        if not collector.connect():
            print("ERRO: Não foi possível conectar ao equipamento")
            return
        
        # Solicita chave pública
        print("\n2. Solicitando chave pública RSA...")
        if not collector.request_public_key():
            print("ERRO: Falha ao obter chave pública")
            return
        
        # Autentica
        print("\n3. Realizando autenticação...")
        if not collector.authenticate(username, password):
            print("ERRO: Falha na autenticação")
            return
        
        # Coleta informações do cabeçalho
        print("\n4. Coletando informações para cabeçalho AFD...")
        employer_info = collector.get_employer_info()
        if employer_info:
            print(f"Informações do empregador: {employer_info}")
        
        rep_info = collector.get_rep_info()
        if rep_info:
            print(f"Informações do REP: {rep_info}")
        
        # serial_info = collector.get_rep_serial_number()
        # if serial_info:
        #     print(f"Número de série: {serial_info}")
        
        # Menu de opções
        print("\n=== OPÇÕES DE COLETA ===")
        print("1. Coletar por NSR (recomendado)")
        print("2. Coletar por endereço de memória")
        print("3. Coletar por data")
        print("4. Coletar todos os métodos")
        
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            result = collector.collect_all_registers("nsr")
        elif choice == "2":
            result = collector.collect_all_registers("memory")
        elif choice == "3":
            # Para data, vamos usar uma data mais recente
            today = datetime.now()
            last_month = today.replace(month=today.month-1 if today.month > 1 else 12)
            start_date = last_month.strftime("%d/%m/%Y 00:00:01")
            
            print(f"\n4. Coletando registros por data (últimos 30 dias)...")
            registers_data = collector.get_registers_by_date(start_date, 50)
            
            if registers_data:
                filename = collector.save_to_afd(registers_data)
                result = (filename, registers_data)
            else:
                result = None
                
        elif choice == "4":
            print("\nColetando com todos os métodos...\n")
            
            # NSR
            result1 = collector.collect_all_registers("nsr")
            time.sleep(2)
            
            # Memory
            result2 = collector.collect_all_registers("memory")
            time.sleep(2)
            
            # Date (último mês)
            today = datetime.now()
            last_month = today.replace(month=today.month-1 if today.month > 1 else 12)
            start_date = last_month.strftime("%d/%m/%Y 00:00:01")
            registers_data = collector.get_registers_by_date(start_date, 1000)
            if registers_data:
                collector.save_to_afd(registers_data, f"registros_rep_evo_date_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            result = "Coleta completa com todos os métodos"
        else:
            print("Opção inválida")
            result = None
        
        if result:
            print(f"\n=== COLETA FINALIZADA COM SUCESSO ===")
            if isinstance(result, tuple):
                print(f"Arquivo salvo: {result[0]}")
        else:
            print(f"\n=== FALHA NA COLETA ===")
        
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        collector.disconnect()
        print("\nScript finalizado.")

if __name__ == "__main__":
    main()