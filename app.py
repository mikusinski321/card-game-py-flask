from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
import random

app = Flask(__name__)

class Card():
    def __init__(self,color,num,ident):
        self.color=color
        self.num=num
        self.ident=ident
class Deck():
    def __init__(self):
        self.cards = list()
        j=0
        for color in ['pink','yellow','red','green']:
            for i in range(10):
                self.cards.append( Card(color,i,j) )
                j+=1
                self.cards.append( Card(color,i,j) )
                j+=1
        random.shuffle(self.cards)
    def draw(self):
        return self.cards.pop()
    def count(self):
        return len(self.cards)
class Game():
    def __init__(self):
        self.players= list()
        self.current_player_id=1
        self.board= Board()
        self.deck= Deck()
        self.phase_amount=1
        self.card_amount=1
        self.phase_list = list()

class Player():
    def __init__(self, name='Anonymous', phase=0,stage=0):
        self.nick=name
        self.type=type
        self.hand=list()
        self.current_phase_id=phase
        self.current_phase_stage=stage
        self.selected=list()
        self.potential_completion=list()
        self.pulled=list()
        self.adding=list()
        score=0
    def findbyid(self,ident):
        for card in self.hand:
            if card.ident==ident:
                return card

class Board():
    def __init__(self):
        self.draw_pile=list()
        self.discard_pile=list()
        self.communicate=''

@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        return hotseat_start(request.form.get('player1'),request.form.get('player2'),request.form.get('card_amount'),request.form.get('phase_amount'))
    return render_template("hotseat/form.htm")

def hotseat_start(player1,player2,card_amount,phase_amount):
    global game
    game = Game()
    game.card_amount=card_amount
    game.phase_amount=phase_amount
    game.players.append( Player(player1) )
    game.players.append( Player(player2) )
    game.board.discard_pile.append ( game.deck.draw() )
    while game.deck.cards:
        game.board.draw_pile.append( game.deck.draw() )
    return redirect('/hotseat/develop', code=302)

@app.route('/hotseat/develop')
def hotseat_develop():
    game.phase_list.clear()
    for player in game.players:
        player.hand.clear()
        player.selected.clear()
        player.pulled.clear()
        player.potential_completion.clear()
        player.current_phase_stage = 0
        for card in player.hand:
            game.board.draw_pile.append(card)
            player.hand.remove(card)
        for i in range(int(game.card_amount)):
            player.hand.append( game.board.draw_pile.pop() )
    game.current_player_id=1
    modes=['run','set','color']
    for i in range(int(game.phase_amount)):
        game.phase_list.append([(random.choice(modes),random.randrange(2, 4)),(random.choice(modes),random.randrange(2, 4))])
    return redirect('/hotseat/next_player', code=302)

@app.route('/hotseat/next_player',methods=['GET','POST'])
def next_player():
    tie_checker()
    if request.form.get('t'):
        game.board.communicate='draw a card from discard or draw pile!'
        return render_template('hotseat/board_2players_drawing.htm', game=game)
    if game.current_player_id != 1:
        game.current_player_id += 1
    else:
        game.current_player_id = 0
    return render_template('hotseat/ready.htm', game=game)

def action_pull_draw():
    game.board.communicate = 'complete a pull or discard a card!'
    if len(game.board.draw_pile) > 0:
        game.players[game.current_player_id].hand.append(game.board.draw_pile.pop())
        return render_template('hotseat/board_2players_pulling.htm', game=game)
    else:
        game.board.communicate = 'draw pile is empty!'
        return render_template('hotseat/board_2players_drawing.htm', game=game)

def action_pull_discard():
    game.board.communicate = 'complete a pull or discard a card!'
    if len(game.board.discard_pile) > 0:
        game.players[game.current_player_id].hand.append(game.board.discard_pile.pop())
        return render_template('hotseat/board_2players_pulling.htm', game=game)
    else:
        game.board.communicate = 'discard pile is empty!'
        return render_template('hotseat/board_2players_drawing.htm', game=game)

def action_discard(card_id=0):
    if len(game.players[game.current_player_id].pulled)<2:
        for cards in game.players[game.current_player_id].pulled:
            for card in cards:
                game.players[game.current_player_id].hand.append(card)
        game.players[game.current_player_id].pulled.clear()

    for card in game.players[game.current_player_id].hand:
        if card.ident == int(card_id):
            game.board.discard_pile.append(card)
            game.players[game.current_player_id].hand.remove(card)
            if len(game.players[game.current_player_id].hand) == 0 and game.players[game.current_player_id].current_phase_stage == len(
                    game.phase_list[game.players[game.current_player_id].current_phase_id]):
                game.players[game.current_player_id].current_phase_id += 1
                if game.players[game.current_player_id].current_phase_id == len(game.phase_list):
                    return render_template('hotseat/vic.htm', game=game)
                else:
                    return render_template('hotseat/roundvic.htm', game=game)
            else:
                return redirect('/hotseat/next_player', code=302)

def action_select(card_id=0):
    game.players[game.current_player_id].selected.append(int(card_id))
    possible_completion_checker(game.players[game.current_player_id].selected)
    return render_template('hotseat/board_2players_pulling.htm', game=game)

def action_deselect(card_id=0):
    game.players[game.current_player_id].selected.remove(int(card_id))
    possible_completion_checker(game.players[game.current_player_id].selected)
    return render_template('hotseat/board_2players_pulling.htm', game=game)

def action_cancel_adding():
    game.players[game.current_player_id].adding.clear()
    return render_template('hotseat/board_2players_pulling.htm', game=game)

def action_completion():
    game.players[game.current_player_id].current_phase_stage += 1
    temp = []
    for card in game.players[game.current_player_id].potential_completion:
        temp.append(card)
        game.players[game.current_player_id].hand.remove(card)
    game.players[game.current_player_id].pulled.append(temp)
    game.players[game.current_player_id].potential_completion.clear()
    game.players[game.current_player_id].selected.clear()
    if game.players[game.current_player_id].current_phase_stage == 2:
        game.board.communicate = "discard a card or complete other players' pull!"
    return render_template('hotseat/board_2players_pulling.htm', game=game)

def action_cancel():
    for cards in game.players[game.current_player_id].pulled:
        for card in cards:
            game.players[game.current_player_id].hand.append(card)
    game.players[game.current_player_id].pulled.clear()
    game.players[game.current_player_id].potential_completion.clear()
    game.players[game.current_player_id].current_phase_stage=0
    return render_template('hotseat/board_2players_pulling.htm', game=game)

def tie_checker():
    counter=40
    for player in game.players:
        if player.pulled:
            for pull in player.pulled:
                counter-=len(pull)
    if counter==0:
        for player in game.players:
            for card in player.hand:
                player.score+=card.num
        if game.players[game.current_player_id].score>game.players[1-game.current_player_id].score:
            game.players[game.current_player_id].current_phase_id+=1
            communicate=f'{game.players[game.current_player_id]} won by points!'
        elif game.players[game.current_player_id].score<game.players[1-game.current_player_id].score:
            game.players[1-game.current_player_id].current_phase_id += 1
            communicate=f'{game.players[1-game.current_player_id]} won by points!'
        else:
            communicate='round ended with a tie!'
        if game.players[game.current_player_id].current_phase_id == len(game.phase_list):
            return render_template('hotseat/vic.htm', game=game)
        elif game.players[game.current_player_id].current_phase_id == len(game.phase_list):
            return render_template('hotseat/vic.htm', game=game)
        else:
            return render_template('hotseat/tie.htm', communicate)

def possible_completion_checker(selected):
    if game.players[game.current_player_id].current_phase_stage < len(game.phase_list[game.players[game.current_player_id].current_phase_id]):
        if len(selected) == game.phase_list[game.players[game.current_player_id].current_phase_id][game.players[game.current_player_id].current_phase_stage][1]:
            temp_num=[]
            temp_col=[]
            temp=[]
            for ident in selected:
                card = game.players[game.current_player_id].findbyid(ident)
                temp_num.append(card.num)
                temp_col.append(card.color)
                temp.append(card)
            if game.phase_list[game.players[game.current_player_id].current_phase_id][game.players[game.current_player_id].current_phase_stage][0] == 'set':
                if len(set(temp_num)) == 1:
                    print('possible completion-set')
                    for ident in temp:
                        game.players[game.current_player_id].potential_completion.append(ident)
            elif game.phase_list[game.players[game.current_player_id].current_phase_id][game.players[game.current_player_id].current_phase_stage][0] == 'run':
                if temp_num == list(range(min(temp_num),max(temp_num)+1)):
                    print('possible completion-run')
                    for ident in temp:
                        game.players[game.current_player_id].potential_completion.append(ident)
            elif game.phase_list[game.players[game.current_player_id].current_phase_id][game.players[game.current_player_id].current_phase_stage][0] == 'color':
                if len(set(temp_col)) == 1:
                    print('possible completion-color')
                    for ident in temp:
                        game.players[game.current_player_id].potential_completion.append(ident)
        else:
            game.players[game.current_player_id].potential_completion.clear()

@app.route('/hotseat/drawing')
@app.route('/hotseat/drawing/<action>')
def hotseat_drawing(action=''):
    if action == 'pull_draw':
        return action_pull_draw()
    elif action == 'pull_discard':
        return action_pull_discard()
    return render_template('hotseat/board_2players_pulling.htm', game=game)

@app.route('/hotseat/adding')
@app.route('/hotseat/adding/<player>/<stage>')
@app.route('/hotseat/adding/<player>/<stage>/<card_id>')
def hotseat_adding(stage=0,player=0,card_id=-1):
    print(player)
    game.players[game.current_player_id].adding.clear()
    stage=int(stage)
    card_id=int(card_id)
    player_id=int(player)
    card=game.players[game.current_player_id].findbyid(card_id)
    if card_id!=-1:
        if game.phase_list[game.players[player_id].current_phase_id][stage][0] == 'run':
            if card.num == (game.players[player_id].pulled[stage][0].num - 1):
                game.players[player_id].pulled[stage].insert(0,card)
            else:
                game.players[player_id].pulled[stage].append(card)
        else:
            game.players[player_id].pulled[stage].append(card)

        game.players[game.current_player_id].hand.remove(card)
        if len(game.players[game.current_player_id].hand) == 0:
            game.players[game.current_player_id].current_phase_id += 1
            if game.players[game.current_player_id].current_phase_id == len(game.phase_list):
                return render_template('hotseat/vic.htm', game=game)
            else:
                return render_template('hotseat/roundvic.htm', game=game)
        return render_template('hotseat/board_2players_pulling.htm', game=game)

        #game.players[game.current_player_id].adding.clear()
    else:
        for card in game.players[game.current_player_id].hand:
            if game.phase_list[game.players[player_id].current_phase_id][stage-1][0] == 'run':
                if card.num == (game.players[player_id].pulled[stage-1][0].num - 1):
                    game.players[game.current_player_id].adding.append([stage-1,card,player_id])
                elif card.num == (game.players[player_id].pulled[stage-1][-1].num + 1):
                    game.players[game.current_player_id].adding.append([stage-1,card,player_id])
            elif game.phase_list[game.players[player_id].current_phase_id][stage-1][0] == 'set':
                if card.num == game.players[player_id].pulled[stage-1][0].num:
                    game.players[game.current_player_id].adding.append([stage-1,card,player_id])
            elif game.phase_list[game.players[player_id].current_phase_id][stage-1][0] == 'color':
                if card.color == game.players[player_id].pulled[stage-1][0].color:
                    game.players[game.current_player_id].adding.append([stage-1,card,player_id])

    return render_template('hotseat/board_2players_adding.htm', game=game)

@app.route('/hotseat/finishing/<action>')
@app.route('/hotseat/finishing/<action>/<card_id>')
def hotseat_finishing(action,card_id=0):
    if action == 'discard':
        return action_discard(card_id)
    elif action == 'select':
        return action_select(card_id)
    elif action == 'deselect':
        return action_deselect(card_id)
    elif action == 'completion':
        return action_completion()
    elif action == 'cancel':
        return action_cancel()
    elif action == 'cancel_adding':
        return action_cancel_adding()
    return render_template('hotseat/board_2players_pulling.htm', game=game)

if __name__ == '__main__':
    app.run(host="wierzba.wzks.uj.edu.pl", port=5123, debug=True)

