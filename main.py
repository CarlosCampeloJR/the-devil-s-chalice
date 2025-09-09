import pyxel

# --- CONFIGURAÇÃO DAS BEBIDAS E RECEITAS ---
# Aumentei a lista para que o jogo tenha mais possibilidades
# Formato: (x, y, largura, altura, cor, nome_do_ingrediente)
BOTTLES = [
    (20, 40, 15, 50, 8, "Vodka"),
    (40, 40, 15, 50, 10, "Suco Laranja"),
    (60, 40, 15, 50, 12, "Suco Cranberry"),
    (80, 40, 15, 50, 9, "Rum"),
    (100, 40, 15, 50, 2, "Licor Azul"),
    (120, 40, 15, 50, 14, "Tequila"),
    (140, 40, 15, 50, 11, "Licor de Cafe"),
]

# Formato: { "name": "Nome do Drink", "ingredients": {"Ingrediente": quantidade}, "feedback": "Texto de sucesso" }
RECIPES = [
    {
        "name": "Screwdriver",
        "ingredients": {"Vodka": 2, "Suco Laranja": 4},
        "feedback": "Um Screwdriver clássico! Perfeito!"
    },
    {
        "name": "Cosmopolitan",
        "ingredients": {"Vodka": 2, "Suco Cranberry": 2},
        "feedback": "Elegante e delicioso. Um Cosmo!"
    },
    {
        "name": "Black Russian",
        "ingredients": {"Vodka": 3, "Licor de Cafe": 2},
        "feedback": "Um Black Russian forte e saboroso."
    },
    {
        "name": "Sea Breeze",
        "ingredients": {"Vodka": 2, "Suco Cranberry": 3, "Suco Laranja": 1},
        "feedback": "Refrescante! Um ótimo Sea Breeze!"
    }
]

class BartenderGame:
    def __init__(self):
        pyxel.init(256, 180, title="Protótipo Bartender", fps=60)
        
        self.reset_drink() # Inicia o jogo com tudo zerado
        pyxel.mouse(True) # Mostra o cursor do mouse
        pyxel.run(self.update, self.draw)

    # --- MÉTODOS DE LÓGICA (UPDATE) ---

    def update(self):
        """Chama o método de update correspondente ao estado atual do jogo."""
        if self.game_state == 'mixing':
            self.update_mixing_state()
        elif self.game_state == 'evaluating':
            self.update_evaluating_state()

    def update_mixing_state(self):
        """Controla a lógica enquanto o jogador está misturando a bebida."""
        # Detecta qual garrafa está sob o mouse
        self.hovered_bottle_index = -1
        for i, (x, y, w, h, color, name) in enumerate(BOTTLES):
            if x < pyxel.mouse_x < x + w and y < pyxel.mouse_y < y + h:
                self.hovered_bottle_index = i
                break

        # Ação de clicar na garrafa para adicionar ingrediente
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.hovered_bottle_index != -1:
            bottle_name = BOTTLES[self.hovered_bottle_index][5]
            self.current_drink[bottle_name] = self.current_drink.get(bottle_name, 0) + 1

        # Lógica dos botões de ação
        # Botão SERVIR
        if 180 < pyxel.mouse_x < 220 and 150 < pyxel.mouse_y < 165 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.evaluate_drink()
        
        # Botão LIMPAR
        if 130 < pyxel.mouse_x < 170 and 150 < pyxel.mouse_y < 165 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.reset_drink()

    def update_evaluating_state(self):
        """No estado de avaliação, apenas espera um clique para recomeçar."""
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.reset_drink()
            
    def evaluate_drink(self):
        """Compara a bebida feita com as receitas e calcula uma pontuação."""
        self.game_state = 'evaluating'
        
        if not self.current_drink:
            self.score = 0
            self.feedback_text = "Você me serviu um copo vazio?!"
            return

        best_score = 0
        best_feedback = "Que mistura bizarra... Tente de novo."

        # Itera sobre cada receita para encontrar a melhor correspondência
        for recipe in RECIPES:
            current_score = 0
            perfect_match = True
            
            # Compara ingredientes da receita com os da bebida do jogador
            for ing, amount in recipe["ingredients"].items():
                player_amount = self.current_drink.get(ing, 0)
                if player_amount > 0:
                    current_score += 10 # Ponto por usar o ingrediente certo
                    if player_amount == amount:
                        current_score += 15 # Bônus por acertar a quantidade
                    else:
                        perfect_match = False
                else:
                    perfect_match = False

            # Penaliza por ingredientes extras
            for ing in self.current_drink:
                if ing not in recipe["ingredients"]:
                    current_score -= 10
            
            if current_score > best_score:
                best_score = current_score
                if perfect_match:
                    best_feedback = recipe["feedback"]
                else:
                    best_feedback = f"Quase um(a) {recipe['name']}..."
        
        self.score = max(0, best_score) # Garante que a nota não seja negativa

        # Define o texto final baseado na pontuação
        if self.score >= 40: # Pontuação para uma receita perfeita (ex: 2 ingredientes = 2*10 + 2*15 = 50)
             self.feedback_text = best_feedback
        elif self.score > 10:
             self.feedback_text = "Chegou perto de algo... mas não sei o que."
        else:
             self.feedback_text = "Isso é... bebível? Acho que não."
             
    def reset_drink(self):
        """Reseta o estado do jogo para começar uma nova bebida."""
        self.game_state = 'mixing'
        self.current_drink = {}
        self.hovered_bottle_index = -1
        self.feedback_text = ""
        self.score = 0

    # --- MÉTODOS DE DESENHO (DRAW) ---

    def draw(self):
        """Limpa a tela e desenha todos os elementos."""
        pyxel.cls(1) # Fundo azul escuro

        # Desenha elementos fixos do cenário
        self.draw_scene()
        
        # Desenha a UI de acordo com o estado do jogo
        if self.game_state == 'mixing':
            self.draw_mixing_ui()
        elif self.game_state == 'evaluating':
            self.draw_evaluating_ui()

    def draw_scene(self):
        """Desenha os elementos que estão sempre na tela."""
        # Balcão
        pyxel.rect(0, 130, 256, 50, 4)
        # Prateleira
        pyxel.rect(10, 90, 160, 5, 4)
        
        # Garrafas
        for i, (x, y, w, h, color, name) in enumerate(BOTTLES):
            pyxel.rect(x, y, w, h, color)
            # Destaque na garrafa sob o mouse
            if i == self.hovered_bottle_index:
                pyxel.rectb(x, y, w, h, 7) # Borda branca

        # Bartender (placeholder)
        pyxel.circ(235, 110, 10, 13) # Cabeça
        pyxel.rect(225, 120, 20, 25, 8) # Corpo

    def draw_mixing_ui(self):
        """Desenha a interface específica do modo de mistura."""
        # Título da garrafa selecionada
        if self.hovered_bottle_index != -1:
            bottle_name = BOTTLES[self.hovered_bottle_index][5]
            pyxel.text(10, 10, f"Garrafa: {bottle_name}", 7)
            
        # Desenha a coqueteleira
        shaker_x, shaker_y, shaker_w, shaker_h = 180, 80, 30, 45
        pyxel.rectb(shaker_x, shaker_y, shaker_w, shaker_h, 7)
        
        # Desenha o líquido na coqueteleira
        total_doses = sum(self.current_drink.values())
        if total_doses > 0:
            fill_height = min(int((total_doses / 10.0) * (shaker_h-2)), shaker_h-2)
            pyxel.rect(shaker_x + 1, shaker_y + (shaker_h-1) - fill_height, shaker_w - 2, fill_height, 12)

        # Lista de ingredientes adicionados
        pyxel.text(10, 110, "Sua Mistura:", 7)
        y_offset = 120
        for ingredient, amount in self.current_drink.items():
            pyxel.text(10, y_offset, f"- {ingredient}: {amount}", 7)
            y_offset += 7

        # Botões
        pyxel.rect(130, 150, 40, 15, 8); pyxel.text(138, 155, "LIMPAR", 0)
        pyxel.rect(180, 150, 40, 15, 11); pyxel.text(188, 155, "SERVIR", 0)

    def draw_evaluating_ui(self):
        """Desenha a interface com o feedback do bartender."""
        # Balão de fala
        text_width = len(self.feedback_text) * 4
        bubble_x, bubble_y = 40, 140
        pyxel.rect(bubble_x, bubble_y, text_width + 10, 25, 7)
        pyxel.text(bubble_x + 5, bubble_y + 5, self.feedback_text, 0)
        pyxel.text(bubble_x + 5, bubble_y + 15, f"Nota: {self.score}", 0)
        
        # Triângulo do balão de fala apontando para o bartender
        pyxel.tri(bubble_x + text_width, bubble_y, bubble_x + text_width + 10, bubble_y+5, 230, 125, 7)
        
        pyxel.text(80, 170, "Clique para fazer outro drink", 5)

# --- Inicia o jogo ---
BartenderGame()