from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models import ParkingLot, ParkingSpot

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

@admin_bp.route('/')
def dashboard():
    lots = ParkingLot.query.all()
    return render_template('admin/dashboard.html', parking_lots=lots)


@admin_bp.route('/lots/create', methods=['POST'])
def create_lot():
    name = request.form['name']
    capacity = int(request.form['capacity'])
    price = float(request.form['price'])
    address = request.form.get('address')
    pin_code = request.form.get('pin_code')

    new_lot = ParkingLot(name=name, capacity=capacity, price=price, address=address, pin_code=pin_code)
    db.session.add(new_lot)
    db.session.commit() # Commit to get the new_lot.id

    for i in range(capacity):
        spot = ParkingSpot(lot_id=new_lot.id, spot_number=i + 1)
        db.session.add(spot)
    
    db.session.commit()

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/lots/<int:lot_id>/edit', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.name = request.form['name']
        new_capacity = int(request.form['capacity'])
        lot.price = float(request.form['price'])
        lot.address = request.form.get('address')
        lot.pin_code = request.form.get('pin_code')

        if new_capacity != lot.capacity:
            # Simple regeneration of spots. For a real app, you'd handle existing reservations.
            ParkingSpot.query.filter_by(lot_id=lot.id).delete()
            for i in range(new_capacity):
                spot = ParkingSpot(lot_id=lot.id, spot_number=i + 1)
                db.session.add(spot)
            lot.capacity = new_capacity

        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_lot.html', lot=lot)


@admin_bp.route('/lots/<int:lot_id>/delete')
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    # Note: Delete will only succeed if all spots are available based on project requirements.
    # We will add that check later. For now, we allow deletion.
    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))
