#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from datetime import datetime, date
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data=[]
  locations = Location.query.all()
  for location in locations:
    venues_list = [];
    venues = location.venues
    for venue in venues:
      venues_list.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(venue.shows)
      })
    data.append({
    "city": location.city,
    "state": location.state,
    "venues": venues_list
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get("search_term")
  venues = Venue.query.all()
  data = []
  for venue in venues:
    name = venue.name
    if name.lower().find(search_term.lower()) != -1:
      data.append({
        "id": venue.id,
        "name": venue.name
      })
  response = {
      "count": len(data),
      "data": data
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)
    location = Location.query.get(venue.location_id)
    past_shows = []
    upcoming_shows = []
    past_shows_query = db.session.query(Show)\
      .join(Venue)\
      .filter(Show.venue_id==venue_id)\
      .filter(Show.start_date<datetime.now()).all()
    upcoming_shows_query = db.session.query(Show)\
      .join(Venue)\
      .filter(Show.venue_id==venue_id)\
      .filter(Show.start_date>datetime.now()).all()
    for show in past_shows_query:
        artist = Artist.query.get(show.artist_id)
        artist_data = {
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_date.strftime('%m/%d/%Y')
        }
        past_shows.append(artist_data)
    for show in upcoming_shows_query:
        artist = Artist.query.get(show.artist_id)
        artist_data = {
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_date.strftime('%m/%d/%Y')
        }
        upcoming_shows.append(artist_data)

    data_list = []
    data_list.append({
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": location.city,
    "state": location.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    })
    data = list(filter(lambda d: d['id'] == venue_id, data_list))[0]
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  data = {"name": request.form.get('name'),
          "city": request.form.get('city'),
          "state": request.form.get('state'),
          "address": request.form.get('address'),
          "genres": request.form.getlist('genres'),
          "facebook_link": request.form.get('facebook_link')
          }
  venue = Venue(name = data["name"], address = data["address"], genres = data["genres"], facebook_link = data["facebook_link"])
  entered_location = Location.query.filter_by(city = data["city"], state = data["state"]).first()
  if entered_location is None:
    location = Location(city = data["city"], state = data["state"])
  else:
    location = entered_location

  try:
    db.session.add(location)
    db.session.add(venue)
    location.venues.append(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' was ussuccessfully listed!')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  Venue.query.get(venue_id).delete()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists = Artist.query.all()
  data=[]
  for artist in artists:
    data.append({
    "id": artist.id,
    "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get("search_term")
  artists = Artist.query.all()
  data = []
  for artist in artists:
    name = artist.name
    if name.lower().find(search_term.lower()) != -1:
      data.append({
        "id": artist.id,
        "name": artist.name
      })

  response = {
      "count": len(data),
      "data": data
    }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  location = Location.query.get(artist.location_id)
  past_shows = []
  upcoming_shows = []
  past_shows_query = db.session.query(Show)\
      .join(Venue)\
      .filter(Show.artist_id==artist_id)\
      .filter(Show.start_date<datetime.now()).all()
  upcoming_shows_query = db.session.query(Show)\
      .join(Venue).\
      filter(Show.artist_id==artist_id)\
      .filter(Show.start_date>datetime.now()).all()
  for show in past_shows_query:
    venue = Venue.query.get(show.venue_id)
    venue_data = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_date.strftime('%m/%d/%Y')
    }
    past_shows.append(venue_data)
  for show in upcoming_shows_query:
    venue = Venue.query.get(show.venue_id)
    venue_data = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_date.strftime('%m/%d/%Y')
    }
    upcoming_shows.append(venue_data)

  data = [{
        'id': artist_id,
        'name': artist.name,
        'genres': artist.genres,
        'city': location.city,
        'state': location.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_talent': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
  }]
  data_list = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data_list)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  print(artist.location_id)
  location = Location.query.get(artist.location_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": location.city,
    "state": location.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  data = {"name": request.form.get('name'),
          "city": request.form.get('city'),
          "state": request.form.get('state'),
          "phone": request.form.get('phone'),
          "genres": request.form.getlist('genres'),
          "facebook_link": request.form.get('facebook_link')
          }
  artist = Artist.query.get(artist_id)
  entered_location = Location.query.filter_by(city = data["city"], state = data["state"]).first()
  if entered_location is None:
    location = Location(city = data["city"], state = data["state"])
  else:
    location = entered_location

  try:
    artist.name = data["name"]
    artist.phone = data["phone"]
    artist.genres = data["genres"]
    artist.facebook_link = data["facebook_link"]
    db.session.add(location)
    location.artists.append(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' was ussuccessfully updated!')
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  location = Location.query.get(venue.location_id)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.name,
    "address": venue.address,
    "city": location.city,
    "state": location.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  data = {"name": request.form.get('name'),
          "city": request.form.get('city'),
          "state": request.form.get('state'),
          "phone": request.form.get('phone'),
          "genres": request.form.getlist('genres'),
          "facebook_link": request.form.get('facebook_link')
          }
  venue = Venue.query.get(venue_id)
  entered_location = Location.query.filter_by(city = data["city"], state = data["state"]).first()
  if entered_location is None:
    location = Location(city = data["city"], state = data["state"])
  else:
    location = entered_location

  try:
    venue.name = data["name"]
    venue.phone = data["phone"]
    venue.genres = data["genres"]
    venue.facebook_link = data["facebook_link"]
    db.session.add(location)
    location.venues.append(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' was ussuccessfully updated!')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  data = {"name": request.form.get('name'),
          "city": request.form.get('city'),
          "state": request.form.get('state'),
          "phone": request.form.get('phone'),
          "genres": request.form.getlist('genres'),
          "facebook_link": request.form.get('facebook_link')
          }
  artist = Artist(name = data["name"], phone = data["phone"], genres = data["genres"], facebook_link = data["facebook_link"])
  entered_location = Location.query.filter_by(city = data["city"], state = data["state"]).first()
  if entered_location is None:
    location = Location(city = data["city"], state = data["state"])
  else:
    location = entered_location

  try:
    db.session.add(location)
    db.session.add(artist)
    location.artists.append(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' was ussuccessfully listed!')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = Show.query.all()
  data=[]
  for show in shows:
    data.append({
      "venues_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": show.start_date.strftime('%m/%d/%Y')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  data = {"artist_id": request.form.get('artist_id'),
          "venue_id": request.form.get('venue_id'),
          "date" : request.form.get('start_time')
          }

  show = Show(artist_id = data["artist_id"], venue_id = data["venue_id"], start_date = data["date"])
  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Show was unsuccessfully listed!')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
