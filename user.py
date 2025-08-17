from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Reservation, ParkingLot, ParkingSpot
from extensions import db
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user', template_folder='templates')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.start_time.desc()).all()
    return render_template('user/dashboard.html', reservations=reservations)

@user_bp.route('/lot/<int:lot_id>')
@login_required
def view_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    return render_template('user/view_lot.html', lot=lot)

@user_bp.route('/book/<int:spot_id>', methods=['POST'])
@login_required
def book_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status == 'O':
        flash('This spot is already occupied.')
        return redirect(url_for('user.view_lot', lot_id=spot.lot_id))

    # Check if user already has an active reservation
    existing_reservation = Reservation.query.filter_by(user_id=current_user.id, end_time=None).first()
    if existing_reservation:
        flash('You already have an active reservation. Please release it before booking a new spot.')
        return redirect(url_for('user.dashboard'))

    spot.status = 'O'
    new_reservation = Reservation(spot_id=spot.id, user_id=current_user.id)
    db.session.add(new_reservation)
    db.session.commit()

    flash('Spot booked successfully!')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/release/<int:reservation_id>', methods=['POST'])
@login_required
def release_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id or reservation.end_time is not None:
        flash('Invalid action.')
        return redirect(url_for('user.dashboard'))

    spot = reservation.spot
    lot = spot.lot

    duration = datetime.utcnow() - reservation.start_time
    hours = (duration.total_seconds() / 3600)
    cost = hours * lot.price 

    reservation.end_time = datetime.utcnow()
    reservation.cost = cost
    spot.status = 'A'

    db.session.commit()

    flash(f'Spot released. Total cost: ${cost:.2f}')
    return redirect(url_for('user.dashboard'))
