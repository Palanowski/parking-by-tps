import subprocess

try:
    # Run the pip --version command
    result = subprocess.run(
    ["pip", "install", "-r", "requirements.txt"],
    capture_output=True,
    text=True,
    check=True
)
    
    # Print the output
    print("Pip Version:", result.stdout.strip())
except subprocess.CalledProcessError as e:
    print("Error executing pip command:", e)