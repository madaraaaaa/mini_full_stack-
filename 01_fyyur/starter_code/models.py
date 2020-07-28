from app import db

class Location(db.Model):
  __tablename__ = 'Location'
  id = db.Column(db.Integer, primary_key=True)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  artists = db.relationship("Artist", backref='location', lazy=True)
  venues = db.relationship("Venue", backref='venue', lazy=True)

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique = True, nullable = False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), unique = True)
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String, unique = True)
    seeking_talent = db.Column(db.String)
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), unique = True)
    location_id = db.Column(db.Integer, db.ForeignKey('Location.id'))
    shows = db.relationship("Show", backref='venues', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
    start_date = db.Column(db.Date, nullable = False)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.String)
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    location_id = db.Column(db.Integer, db.ForeignKey('Location.id'))
    shows = db.relationship("Show", backref='artists', lazy=True)

