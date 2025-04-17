from PIL import Image, ImageDraw, ImageFont
import os

# Criar diretório para placeholder se não existir
os.makedirs('frontend/static/images/placeholder', exist_ok=True)

# Criar imagem placeholder para usuário
def create_user_placeholder():
    # Tamanho da imagem
    width, height = 200, 200
    
    # Cores
    background_color = (240, 240, 240)  # Cinza claro
    rectangle_color = (200, 200, 200)   # Cinza médio
    text_color = (120, 120, 120)        # Cinza escuro
    
    # Criar imagem com fundo cinza claro
    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)
    
    # Desenhar retângulo cinza médio como fundo
    draw.rectangle([(20, 20), (width-20, height-20)], fill=rectangle_color)
    
    # Adicionar símbolo de usuário (cabeça e ombros simplificados)
    # Círculo para a cabeça
    draw.ellipse([(width//2-30, 50), (width//2+30, 110)], fill=background_color)
    
    # Retângulo para o corpo
    draw.rectangle([(width//2-40, 110), (width//2+40, 170)], fill=background_color, radius=20)
    
    # Tentar adicionar texto "User"
    try:
        # Se a fonte estiver disponível
        font = ImageFont.truetype("arial", 20)
        text = "User"
        text_width = font.getlength(text)
        draw.text((width//2-text_width//2, height-35), text, font=font, fill=text_color)
    except Exception:
        # Se não encontrar a fonte, usar a padrão
        draw.text((width//2-20, height-35), "User", fill=text_color)
    
    # Salvar a imagem
    img.save('frontend/static/images/placeholder/user.jpg')
    print("Imagem placeholder de usuário criada com sucesso!")

if __name__ == "__main__":
    create_user_placeholder() 