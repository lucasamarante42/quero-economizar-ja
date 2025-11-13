import subprocess
import sys

def install_package(package):
	try:
		subprocess.check_call([sys.executable, "-m", "pip", "install", package])
		print(f"✅ {package} instalado com sucesso")
		return True
	except subprocess.CalledProcessError:
		print(f"❌ Falha ao instalar {package}")
		return False

# Lista de dependências principais
dependencies = [
	"fastapi==0.100.0",
	"uvicorn==0.22.0",
	"pymongo==4.3.3",
	"pydantic==1.10.7",
	"python-multipart==0.0.6",
	"pypdf2==3.0.1",
	"pdfplumber==0.9.0",
	"requests==2.28.2",
	"pandas==1.5.3",
	"numpy==1.24.3",
	"prometheus-client==0.16.0",
	"motor==3.1.2"
]

print("Instalando dependências...")
success_count = 0

for package in dependencies:
	if install_package(package):
		success_count += 1

print(f"\n✅ {success_count}/{len(dependencies)} dependências instaladas com sucesso!")

if success_count == len(dependencies):
	print("🎉 Todas as dependências foram instaladas!")
else:
	print("⚠️  Algumas dependências podem ter falhado. Verifique acima.")