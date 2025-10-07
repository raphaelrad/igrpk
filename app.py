from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)
CORS(app)  # Permitir requisições do base44

def consultar_placa_selenium(placa):
    """
    Consulta dados do veículo no placafipe.com.br usando Selenium
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Modo invisível
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        url = f'https://placafipe.com.br/placa/{placa}'
        
        print(f"Acessando: {url}")
        driver.get(url)
        
        # Aguardar carregamento da página (até 10 segundos)
        wait = WebDriverWait(driver, 10)
        
        # Aguardar elementos carregarem
        time.sleep(3)
        
        # Capturar dados usando XPath
        marca = ""
        modelo = ""
        cor = ""
        
        try:
            # XPath para Marca
            marca_element = driver.find_element(By.XPATH, "//p[strong[contains(text(), 'Marca:')]]")
            marca = marca_element.text.replace("Marca:", "").strip()
        except:
            print("Marca não encontrada")
        
        try:
            # XPath para Modelo
            modelo_element = driver.find_element(By.XPATH, "//p[strong[contains(text(), 'Modelo:')]]")
            modelo = modelo_element.text.replace("Modelo:", "").strip()
        except:
            print("Modelo não encontrado")
        
        try:
            # XPath para Cor
            cor_element = driver.find_element(By.XPATH, "//p[strong[contains(text(), 'Cor:')]]")
            cor = cor_element.text.replace("Cor:", "").strip()
        except:
            print("Cor não encontrada")
        
        # Verificar se encontrou dados válidos
        if marca and modelo and cor:
            return {
                "sucesso": True,
                "marca": marca,
                "modelo": modelo,
                "cor": cor
            }
        else:
            return {
                "sucesso": False,
                "erro": "Dados incompletos ou placa não encontrada"
            }
            
    except Exception as e:
        print(f"Erro: {str(e)}")
        return {
            "sucesso": False,
            "erro": f"Erro ao consultar placa: {str(e)}"
        }
    
    finally:
        if driver:
            driver.quit()

@app.route('/api/consultar-placa', methods=['POST'])
def consultar_placa():
    """
    Endpoint para consultar placa
    Body: { "placa": "ABC1234" }
    """
    try:
        data = request.get_json()
        placa = data.get('placa', '').strip().upper()
        
        if not placa or len(placa) != 7:
            return jsonify({
                "sucesso": False,
                "erro": "Placa inválida. Use formato ABC1234"
            }), 400
        
        resultado = consultar_placa_selenium(placa)
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            "sucesso": False,
            "erro": f"Erro no servidor: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({"status": "ok", "message": "Servidor funcionando"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)