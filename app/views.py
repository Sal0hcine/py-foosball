from app import app, db, models, socketio
from flask import jsonify, request, abort
import datetime

@app.route('/')
def index():
    return "I've been expecting you..."

# Get all matches
@app.route("/api/v1.0/matches", methods=['GET'])
def get_matches():
    matches = []
    for match in models.Match.query.all():
        matches.append({'id': match.id,
                        'date': match.date,
                        'team1score': match.team1score,
                        'team2score': match.team2score,
                        'complete': match.complete})
    return jsonify({'matches': matches})

# Get match details
@app.route("/api/v1.0/matches/<int:match_id>", methods=['GET'])
def get_match(match_id):
    m = models.Match.query.get(int(match_id))

    goals = []
    for goal in models.Goal.query.filter_by(matchId=match_id).join(models.Player).all():
        if goal.playerId is not None:
            goals.append({'id': goal.id,
                          'matchId': goal.matchId,
                          'playerId': goal.playerId,
                          'player': goal.player.name,
                          'pos': goal.position})

    match = [{'id': m.id,
                    'date': m.date,
                    'team1score': m.team1score,
                    'team2score': m.team2score,
                    'complete': m.complete,
                    'goals': goals}]
    return jsonify({'match': match})

# Create a match
@app.route("/api/v1.0/match", methods=['POST'])
def create_match():
    now = datetime.datetime.now()
    match = models.Match(date=now, team1score=0, team2score=0)
    db.session.add(match)
    db.session.commit()

    return jsonify({'id': match.id}), 201

# Update a match
@app.route("/api/v1.0/match/goal", methods=['POST'])
def update_match():
    if not request.json or not 'team' in request.json:
        return jsonify({'error': 'missing `team` field in request'}), 200

    m = models.Match.query.order_by(models.Match.id.desc()).first()

    if m.team1score != 10 and m.team2score != 10:

        if request.json['team'] == 1:
            m.team1score += 1
        elif request.json['team'] == 2:
            m.team2score += 1

        if m.team1score == 9 and m.team2score == 9:
            m.team1score = 8
            m.team2score = 8

        if m.team1score == 10 or m.team2score == 10:
            m.complete = True

        latestGoal = models.Goal(date=datetime.datetime.now(), matchId=m.id)
        db.session.add(latestGoal)

        db.session.commit()

    match = [{'id': m.id,
              'date': m.date,
              'team1score': m.team1score,
              'team2score': m.team2score,
              'complete': m.complete}]

    socketio.emit('scores', {'team1score': m.team1score, 'team2score': m.team2score}, namespace='/scores')

    return jsonify({'match': match})

# Create player
@app.route("/api/v1.0/player", methods=['POST'])
def create_player():
    if not request.json or not 'name' in request.json:
        return jsonify({'error': 'missing `name` field in request'}), 200

    player = models.Player(name=request.json['name'])
    db.session.add(player)
    db.session.commit()

    return jsonify({'id': player.id}), 201

# Get players
@app.route("/api/v1.0/players", methods=['GET'])
def get_players():
    players = []
    for player in models.Player.query.all():
        players.append({'id': player.id,
                        'name': player.name})

    return jsonify({'players': players})

# Get players
@app.route("/api/v1.0/players/<int:player_id>", methods=['GET'])
def get_player(player_id):
    player = models.Player.query.get(player_id)

    goals = []
    for goal in models.Goal.query.filter_by(playerId=player_id):
        if goal.playerId is not None:
            goals.append({'id': goal.id,
                          'matchId': goal.matchId,
                          'playerId': goal.playerId,
                          'pos': goal.position})

    return jsonify({'player': {'id': player.id,
                    'name': player.name,
                               'goals': goals}})


# Get players
@app.route("/api/v1.0/goals", methods=['GET'])
def get_goals():
    goals = []
    for goal in models.Goal.query.all():
        goals.append({'id': goal.id,
                        'matchId': goal.matchId,
                      'playerId': goal.playerId,
                      'pos': goal.position})

    return jsonify({'goals': goals})

@app.route("/api/v1.0/goals/claim", methods=['POST'])
def claim_goals():

    if not request.json or not 'playerId' in request.json:
        return jsonify({'error': 'missing `playerId` field in request'}), 200

    goal = models.Goal.query.order_by(models.Goal.id.desc()).first()

    goal.playerId = request.json['playerId']
    goal.position = request.json['pos']
    goal.ownGoal = request.json['ownGoal']

    db.session.commit()

    return jsonify({'goal': {'id': goal.id, 'matchId': goal.matchId, 'playerId': goal.playerId}})

@socketio.on('connect', namespace='/scores')
def get_current_score():
    m = models.Match.query.order_by(models.Match.id.desc()).first()
    socketio.emit('connect', {'team1score': m.team1score, 'team2score': m.team2score}, namespace='/scores')
