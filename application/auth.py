from flask import Blueprint, redirect, render_template, request, url_for, flash
from application.models import *
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return render_template('index.html')

@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        this_user = User.query.filter_by(email=email).first()

        if this_user:
            if this_user.password == password:
                if this_user.status == 'blacklist':
                    return render_template('login.html', error = "You'r are blacklisted.")
                elif this_user.role == 'admin':
                    return redirect(url_for('auth.admin'))
                elif this_user.role == 'staff' and this_user.status != "approved":
                    return render_template('login.html', error = "Your Registration is Pending.")
                elif this_user.role == 'staff':
                    staff_profile = Staff.query.filter_by(user_id=this_user.id).first()
                    if not staff_profile:
                        staff_profile = Staff(user_id=this_user.id, phone="", about="", location="", experience="")
                        db.session.add(staff_profile)
                        db.session.commit()
                    return redirect(url_for('auth.staff', staff_id=staff_profile.id))
                elif this_user.role == 'trekker':
                    trekker_profile = Trekker.query.filter_by(user_id=this_user.id).first()
                    if not trekker_profile:
                        trekker_profile = Trekker(user_id=this_user.id, phone="", about="", location="", trekking_experience="")
                        db.session.add(trekker_profile)
                        db.session.commit()
                    return redirect(url_for('auth.trekker', trekker_id=trekker_profile.id))
                else:
                    return redirect(url_for('auth.login'))
            else:
                return render_template('login.html', error = "Incorrect Password")
        else:
            return render_template('login.html', error = "First register to the portal, then try to login.")
    return render_template('login.html')

@auth_bp.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == "POST":
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        role = request.form.get('role')
        if password != cpassword:
            return render_template('register.html', error='Passwords do not match')
        user_email = User.query.filter_by(email=email).first()
        if user_email:
            return render_template('register.html', error="Email is already exists.")
        else:
            status = 'approved' if role == 'admin' or role == 'trekker' else 'pending'
            new_user = User(fullname=fullname, email=email, password=password, role=role, status=status)
            db.session.add(new_user)
            db.session.flush()

            if role == 'staff':
                staff_profile = Staff(user_id=new_user.id, phone="", about="", location="", experience="")
                db.session.add(staff_profile)
            elif role == 'trekker':
                trekker_profile = Trekker(user_id=new_user.id, phone="", about="", location="", trekking_experience="")
                db.session.add(trekker_profile)

            db.session.commit()
            return redirect(url_for('auth.login'))
    return render_template('register.html')


#Admin Routes

@auth_bp.route('/admin')
def admin():
    this_user = User.query.filter_by(role='admin').first()
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    total_booking = Booking.query.count()
    total_trek = Trek.query.count()
    total_trekker = Trekker.query.count()
    total_staff = Staff.query.count()
    return render_template('templates/admin/admin_dashboard.html', this_user=this_user,
                           bookings=bookings, total_booking=total_booking,
                           total_trek=total_trek, total_staff=total_staff,
                           total_trekker=total_trekker)


@auth_bp.route('/admin_approve_booking/<int:id>')
def approve_booking(id):
    booking = Booking.query.get(id)
    if booking:
        booking.status = 'Approve'
        db.session.commit()
    return redirect(url_for('auth.admin'))  

@auth_bp.route('/admin_reject_booking/<int:id>')
def reject_booking(id):
    booking = Booking.query.get(id)
    if booking:
        booking.status = 'Reject'
        db.session.commit()
    return redirect(url_for('auth.admin'))

@auth_bp.route('/admin_trek', endpoint='admin_trek')
def trek():
    this_user = User.query.filter_by(role='admin').first()
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('templates/admin/admin_manage_trek.html', this_user=this_user, bookings=bookings)


@auth_bp.route('/admin_add_trek', methods=['GET', 'POST'], endpoint='admin_add_trek')
def add_trek():
    if request.method == 'POST':
        trekname = request.form.get('trekname')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        slots = request.form.get('slots')
        description = request.form.get('des')
        status = request.form.get('status')
        start_date = request.form.get('sdate')
        end_date = request.form.get('edate')
        staff_id = request.form.get('staff_id')

        try:
            duration = int(duration) if duration not in (None, '') else 0
            slots = int(slots) if slots not in (None, '') else 0
            start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        except ValueError:
            duration = 0
            slots = 0
            start_date = None
            end_date = None

        # resolve staff assignment
        staff_id_val = int(staff_id) if staff_id not in (None, '') else None

        sname_val = ''
        if staff_id_val:
            staff_obj = Staff.query.get(staff_id_val)
            if staff_obj:
                sname_val = staff_obj.user.fullname

        new_trek = Trek(trekname=trekname, location=location,
                        difficulty=difficulty, duration=str(duration),
                        slots=slots, status=status, sname=sname_val,
                        description=description, start_date=start_date, end_date=end_date,
                        staff_id=staff_id_val)
        db.session.add(new_trek)
        db.session.commit()
        return redirect(url_for('auth.admin_trek'))

    staff_list = Staff.query.join(User).all()
    return render_template('templates/admin/admin_add_trek.html', staff_list=staff_list)


# Admin Staff Manage
@auth_bp.route('/admin_manage_staff')
def admin_manage_staff():
    pending_staffs = Staff.query.join(User).filter(User.status == 'pending', User.role == 'staff').all()
    active_staffs = Staff.query.join(User).filter(User.status == 'approved', User.role == 'staff').all()
    blacklisted_staffs = Staff.query.join(User).filter(User.status == 'blacklist', User.role == 'staff').all()
    return render_template('templates/admin/admin_manage_staff.html', pending_staffs=pending_staffs,
        active_staffs=active_staffs,
        blacklisted_staffs=blacklisted_staffs)


@auth_bp.route('/approve_staff/<int:id>')
def approve_staff(id):
    staff = Staff.query.get(id)
    if staff:
        staff.user.status = 'approved'
        db.session.commit()
    return redirect(url_for('auth.admin_manage_staff'))

@auth_bp.route('/blacklist_staff/<int:id>')
def blacklist_staff(id):
    staff = Staff.query.get(id)
    if staff:
        staff.user.status = 'blacklist'
        db.session.commit()
    return redirect(url_for('auth.admin_manage_staff'))


@auth_bp.route('/restore_staff/<int:id>')
def restore_staff(id):
    staff = Staff.query.get(id)
    if staff:
        staff.user.status = 'approved'
        db.session.commit()
    return redirect(url_for('auth.admin_manage_staff'))


@auth_bp.route('/admin_manage_trekker', endpoint='admin_manage_trekker')
def admin_manage_trekker():
    trekkers = Trekker.query.join(User).filter(User.role == 'trekker').all()
    return render_template('templates/admin/admin_manage_users.html', trekkers=trekkers)


@auth_bp.route('/admin_blacklist_trekker/<int:id>')
def admin_blacklist_trekker(id):
    trekker = Trekker.query.get(id)
    if trekker:
        trekker.user.status = 'blacklist'
        db.session.commit()
    return redirect(url_for('auth.admin_manage_trekker'))


@auth_bp.route('/admin_manage_booking', endpoint='admin_manage_booking')
def admin_manage_booking():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('templates/admin/admin_bookings.html', bookings=bookings)


@auth_bp.route('/admin_blacklist_booking/<int:id>') #, endpoint='admin_manage_bookings'
def admin_blacklist_booking(id):
    booking = Booking.query.get(id)
    if booking:
        booking.status = 'blacklist'
        db.session.commit()
    return redirect(url_for('auth.admin_manage_booking'))



@auth_bp.route('/staff/<int:staff_id>')
def staff(staff_id):
    staff_profile = Staff.query.get(staff_id)
    if not staff_profile:
        staff_profile = Staff.query.filter_by(user_id=staff_id).first()
    if not staff_profile:
        return redirect(url_for('auth.login'))
    my_assigned_trek = Trek.query.filter_by(staff_id=staff_profile.id).all()
    total_assigned_trek = len(my_assigned_trek)
    open_treks = Trek.query.filter_by(staff_id=staff_profile.id, status="Open").count()
    total_bookings = sum(len(trek.bookings) for trek in staff_profile.assigned_trek)
    total_trekkers = len({booking.user_id for trek in staff_profile.assigned_trek for booking in trek.bookings})
    return render_template('templates/staff/staff_dashboard.html', staff_profile=staff_profile,
                           total_assigned_trek=total_assigned_trek, open_treks=open_treks,
                           total_bookings=total_bookings, total_trekkers=total_trekkers,
                           my_assigned_trek=my_assigned_trek)


@auth_bp.route('/staff/<int:staff_id>/staff_manage_trek/<int:trek_id>', methods = ['GET', 'POST'])
def staff_manage_trek(staff_id, trek_id):
    staff_profile = Staff.query.get(staff_id)
    trek = Trek.query.filter_by(id=trek_id, staff_id=staff_id).first()
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    if request.method == "POST":
        trek.slots = request.form.get('slots')
        trek.status = request.form.get('status')
        db.session.commit()
        
        return redirect(url_for('auth.staff', staff_id=staff_id))
    my_assigned_trek = Trek.query.filter_by(staff_id=staff_profile.id).all()
    return render_template('templates/staff/staff_manage_trek.html', staff_profile=staff_profile,
                           trek=trek, bookings=bookings, my_assigned_trek=my_assigned_trek)


@auth_bp.route('/staff_profile/<int:staff_id>')
def staff_profile(staff_id):
    staff_profile = Staff.query.get(staff_id)
    if not staff_profile:
        return redirect(url_for('auth.login'))
    my_assigned_trek = Trek.query.filter_by(staff_id=staff_profile.id).all()
    return render_template('templates/staff/staff_profile.html', staff_profile=staff_profile, my_assigned_trek=my_assigned_trek)


@auth_bp.route('/staff_edit_profile/<int:staff_id>', methods=['GET', 'POST'])
def staff_edit_profile(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        staff.user.fullname = request.form.get('fullname')
        staff.phone = request.form.get('phone')
        staff.location = request.form.get('loc')
        staff.experience = request.form.get('experience')
        staff.about = request.form.get('about')
        db.session.commit()
        
        return redirect(url_for('auth.staff_profile', staff_id=staff_id))
    my_assigned_trek = Trek.query.filter_by(staff_id=staff.id).all()
    return render_template('templates/staff/staff_edit_profile.html', staff=staff, staff_profile=staff, my_assigned_trek=my_assigned_trek)


# Trekker Routes

@auth_bp.route('/trekker/<int:trekker_id>')
def trekker(trekker_id):
    trekker_profile = Trekker.query.get(trekker_id)
    if not trekker_profile:
        trekker_profile = Trekker.query.filter_by(user_id=trekker_id).first()
    if not trekker_profile:
        return redirect(url_for('auth.login'))

    treks = Trek.query.filter(Trek.status.in_(['Open', 'Upcoming', 'Approved'])).all()
    my_bookings = Booking.query.filter_by(user_id=trekker_id).all()
    return render_template('templates/user/user_dashboard.html', trekker_profile=trekker_profile, treks=treks, my_bookings=my_bookings)


@auth_bp.route('/trekker/<int:trekker_id>/view_trek/<int:trek_id>')
def view_trek(trekker_id, trek_id):
    trekker_profile = Trekker.query.get(trekker_id)
    trek = Trek.query.get(trek_id)
    return render_template('templates/user/user_trek.html', trekker_profile=trekker_profile, book_trek=book_trek)

@auth_bp.route('/trekker/<int:trekker_id>/book_trek/<int:trek_id>')
def book_trek(trekker_id, trek_id):
    book_trek = Trek.query.get(trek_id)
    if book_trek:
        book_trek.status = 'booked'
        db.session.commit()
        return redirect(url_for('auth.trekker', id=trekker_id))

@auth_bp.route('/trekker_profile/<int:trekker_id>')
def trekker_profile(trekker_id):
    trekker= Trekker.query.get(trekker_id)
    return render_template('templates/user/user_profile.html', trekker=trekker)

@auth_bp.route('/trekker_edit_profile/<int:trekker_id>', methods=['GET','POST'])
def trekker_edit_profile(trekker_id):
    trekker= Trekker.query.get(trekker_id)
    if not trekker:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        trekker.user.fullname = request.form.get('fullname')
        trekker.phone = request.form.get('phone')
        trekker.location = request.form.get('loc')
        trekker.about = request.form.get('about')
        trekker.trekking_experience = request.form.get('texp')
        db.session.commit()
        return redirect(url_for('auth.trekker_profile', id=trekker_id))
    return render_template('templates/user/user_edit_profile.html', trekker=trekker)

@auth_bp.route('/trekker_history/<int:trekker_id>')
def trekker_history(trekker_id):
    mybooking = Booking.query.filter(user_id=trekker_id, status ='Completed').all()
    return render_template('templates/user/user_history.html', mybooking=mybooking)

def format_date(value):
    if value:
        return value.strftime("%d %B %Y")
    return ""