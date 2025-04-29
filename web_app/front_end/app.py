import os
import sys
from bson import ObjectId
from flask import (
    Flask, render_template, request,
    session, redirect, url_for, flash
)
import random

# ── import back_end packages ──
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)
from back_end.mongo_connection import RecipeDatabase

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_me")

# ── connect to MongoDB ──────────────────────────────────────────────
db = RecipeDatabase()
if not db.connect():
    raise RuntimeError("Failed to connect to MongoDB Atlas!")
user_coll  = db.db['user_information']
saved_coll = db.db['saved_recipes']
temp_coll = db.db['temp_recommendations']

# ── require login for everything except these endpoints ──────────────
@app.before_request
def require_login():
    if request.endpoint not in (
        'login','sign_up','static'
    ) and 'username' not in session:
        return redirect(url_for('login'))

# ── AUTH ─────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password']
        user = user_coll.find_one({'username':u})
        if user and user.get('password') == p:
            session['username'] = u
            flash("Logged in successfully.", "success")
            return redirect(url_for('main'))
        flash("Invalid username or password", "danger")
    return render_template('login.html')

@app.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password']
        user_coll.insert_one({'username':u,'password':p})
        session['username'] = u
        flash("Account created!", "success")
        return redirect(url_for('main'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# ── MAIN MENU & SAVED LIST ──────────────────────────────────────────
@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/saved_recipes')
def saved_recipes():
    saved_docs = list(saved_coll.find({'user': session['username']}))
    saved_ids  = [d['recipe_id'] for d in saved_docs]
    recipes    = list(db.collection.find({'_id': {'$in': saved_ids}}))
    return render_template('saved.html', saved=recipes)

# ── SAVE / UNSAVE ───────────────────────────────────────────────────
@app.route('/save_recipe/<recipe_id>', methods=['POST'])
def save_recipe(recipe_id):
    saved_coll.insert_one({
        'user': session['username'],
        'recipe_id': ObjectId(recipe_id)
    })
    flash("Recipe saved!", "success")
    return redirect(request.referrer or url_for('main'))

@app.route('/unsave_recipe/<recipe_id>', methods=['POST'])
def unsave_recipe(recipe_id):
    saved_coll.delete_one({
        'user': session['username'],
        'recipe_id': ObjectId(recipe_id)
    })
    flash("Removed from saved recipes", "info")
    return redirect(request.referrer or url_for('saved_recipes'))

# ── VIEW A SINGLE RECIPE ────────────────────────────────────────────
@app.route('/view_recipe/<recipe_id>')
def view_recipe(recipe_id):
    recipe = db.collection.find_one({'_id': ObjectId(recipe_id)})

    # Get list of cuisine images
    cuisine_img_folder = os.path.join(app.static_folder, 'images/cuisines')
    available_images = [
        f for f in os.listdir(cuisine_img_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    # Randomly select one
    recipe_img = random.choice(available_images) if available_images else 'default.jpg'

    return render_template("view.html", recipe=recipe, recipe_img=recipe_img)



# ── QUIZ PAGES ───────────────────────────────────────────────────────
@app.route('/')
def home():
    return redirect(url_for('main'))

@app.route('/page1', methods=['GET', 'POST'])
def page1():
    if request.method == 'POST':
        selected = request.form.getlist('dietary_preferences[]')
        
        if not selected:
            flash("Please select at least one dietary or allergy option.", "warning")
            return render_template('page1.html', response1=session.get('response1', []))
        
        session['response1'] = selected
        return redirect(url_for('page2'))

    return render_template('page1.html', response1=session.get('response1', []))




@app.route('/page2', methods=['GET','POST'])
def page2():
    if request.method == 'POST':
        if 'previous' in request.form:
            return redirect(url_for('page1'))
        choice = request.form.get('response2')
        if not choice:
            flash("Please select a calorie range.", "warning")
            return render_template('page2.html', response2='')
        session['response2'] = choice
        return redirect(url_for('page3'))
    return render_template('page2.html',
                           response2=session.get('response2',''))


@app.route('/page3', methods=['GET','POST'])
def page3():
    if request.method == 'POST':
        if 'previous' in request.form:
            return redirect(url_for('page2'))
        choice = request.form.get('response3')
        if not choice:
            flash("Please select a time range.", "warning")
            return render_template('page3.html', response3='')
        session['response3'] = choice
        return redirect(url_for('page4'))
    return render_template('page3.html',
                           response3=session.get('response3',''))


@app.route('/page4', methods=['GET','POST'])
def page4():
    if request.method == 'POST':
        selected = request.form.getlist('response4[]')
        print(selected)
        if not selected:
            flash("Please select at least one cuisine.", "warning")
            return render_template('page4.html', response4=[])
        session['response4'] = selected
        return redirect(url_for('page5'))
    return render_template('page4.html',
                           response4=session.get('response4', []))


@app.route('/page5', methods=['GET','POST'])
def page5():
    if request.method == 'POST':
        choice = request.form.get('response5')
        print(choice)
        if not choice:
            flash("Please indicate your cooking skill level.", "warning")
            return render_template('page5.html', response5='')
        session['response5'] = choice
        return redirect(url_for('page6'))
    return render_template('page5.html',
                           response5=session.get('response5', ''))


@app.route('/page6', methods=['GET','POST'])
def page6():
    if request.method == 'POST':
        selected = request.form.getlist('response6[]')
        print(selected)
        if not selected:
            flash("Please select at least one meal type.", "warning")
            return render_template('page6.html', response6=[])
        session['response6'] = selected
        return redirect(url_for('page7'))
    return render_template('page6.html',
                           response6=session.get('response6', []))


""" @app.route('/page7', methods=['GET','POST'])
def page7():
    if request.method=='POST':
        session['response7'] = request.form.getlist('response7[]')
        session.pop('recommendations', None)  # 💥 Clear old recommendations here
        if 'recommendations' in session:
            print(session['recommendations'])
        else:
            print("Not in session")
        return redirect(url_for('results'))
    return render_template('page7.html', response7=session.get('response7', [])) """

@app.route('/page7', methods=['GET','POST'])
def page7():
    if request.method == 'POST':
        session['response7'] = request.form.getlist('response7[]')

        # Clear any old recommendation data from MongoDB
        temp_coll = db.db['temp_recommendations']
        temp_coll.delete_many({
            "user": session['username'],
            "type": "quiz_result"
        })

        return redirect(url_for('results'))

    return render_template('page7.html', response7=session.get('response7', []))




# ── RESULTS ───────────────────────────────────────────────────────────
import os
import random
from flask import render_template, session, flash
from back_end.recipe_system import RecipeRecommendationSystem

""" @app.route('/results')
def results():
    if 'recommendations' not in session:
        prefs = {
            'question1': session.get('response1', []),
            'question2': session.get('response2', None),
            'question3': session.get('response3', None),
            'question4': session.get('response4', []),
            'question5': session.get('response5', None),
            'question6': session.get('response6', []),
            'question7': session.get('response7', [])
        }

        rec_sys = RecipeRecommendationSystem()
        if not rec_sys.connected:
            flash("Cannot reach recommendation engine", "danger")
            recommendations = {}
        else:
            recommendations = rec_sys.get_recommendations(prefs)

            # Convert ObjectIds to strings for session storage
            for meal, recs in recommendations.items():
                for r in recs:
                    if '_id' in r:
                        r['_id'] = str(r['_id'])

            session['recommendations'] = recommendations
    else:
        print(session['recommendations'])
        recommendations = session['recommendations']

    # 🔁 Assign random, unique cuisine images to each recipe
    cuisine_img_folder = os.path.join(app.static_folder, 'images/cuisines')
    available_images = [
        f for f in os.listdir(cuisine_img_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    random.shuffle(available_images)

    all_recipes = [r for recs in recommendations.values() for r in recs]
    image_map = {}
    for i, recipe in enumerate(all_recipes):
        assigned_img = available_images[i % len(available_images)]
        image_map[str(recipe['_id'])] = assigned_img

    return render_template(
        'results.html',
        recommendations=recommendations,
        image_map=image_map,
        prefs={
            'question1': session.get('response1', []),
            'question2': session.get('response2', None),
            'question3': session.get('response3', None),
            'question4': session.get('response4', []),
            'question5': session.get('response5', None),
            'question6': session.get('response6', []),
            'question7': session.get('response7', [])
        }
    )
 """

@app.route('/results')
def results():
    # MongoDB collection for temporary quiz results
    temp_coll = db.db['temp_recommendations']

    # Try to load from MongoDB
    saved_doc = temp_coll.find_one({
        "user": session['username'],
        "type": "quiz_result"
    })

    if saved_doc:
        recommendations = saved_doc['data']
    else:
        # Generate preferences from session
        prefs = {
            'question1': session.get('response1', []),
            'question2': session.get('response2', None),
            'question3': session.get('response3', None),
            'question4': session.get('response4', []),
            'question5': session.get('response5', None),
            'question6': session.get('response6', []),
            'question7': session.get('response7', [])
        }

        rec_sys = RecipeRecommendationSystem()
        if not rec_sys.connected:
            flash("Cannot reach recommendation engine", "danger")
            recommendations = {}
        else:
            recommendations = rec_sys.get_recommendations(prefs)

            # Convert ObjectIds to strings for JSON storage
            for meal, recs in recommendations.items():
                for r in recs:
                    if '_id' in r:
                        r['_id'] = str(r['_id'])

            # Store recommendations in MongoDB
            temp_coll.delete_many({
                "user": session['username'],
                "type": "quiz_result"
            })
            temp_coll.insert_one({
                "user": session['username'],
                "type": "quiz_result",
                "data": recommendations
            })

    # 🔁 Assign random images for display
    cuisine_img_folder = os.path.join(app.static_folder, 'images/cuisines')
    available_images = [
        f for f in os.listdir(cuisine_img_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    random.shuffle(available_images)

    all_recipes = [r for recs in recommendations.values() for r in recs]
    image_map = {}
    for i, recipe in enumerate(all_recipes):
        assigned_img = available_images[i % len(available_images)]
        image_map[str(recipe['_id'])] = assigned_img

    return render_template(
        'results.html',
        recommendations=recommendations,
        image_map=image_map,
        prefs={
            'question1': session.get('response1', []),
            'question2': session.get('response2', None),
            'question3': session.get('response3', None),
            'question4': session.get('response4', []),
            'question5': session.get('response5', None),
            'question6': session.get('response6', []),
            'question7': session.get('response7', [])
        }
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
