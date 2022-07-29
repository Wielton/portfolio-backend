from app import app
from flask import jsonify, request
from db_helpers import *
import uuid




@app.post('/api/user')
def user_post():
    data = request.json
    first_name = data.get('firstName')
    company_name = data.get('companyName')
    email = data.get('email')
    comment = data.get('comment')
    if not first_name:
        return jsonify("First Name required"), 422
    if not email:
        return jsonify("Email required"), 422
    if not comment:
        return jsonify("You didn't leave a comment!"), 422
    run_query("INSERT INTO messages(first_name, company_name, email, comment) VALUES (?,?,?,?)", [first_name, company_name, email,comment])
    
    
    return jsonify("Thanks for the review!!"),201  
# Manager redirected to logged-in where they see  


@app.patch('/api/manager')
def edit_profile():
    # GET params for session check
    params = request.args
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 401
    manager_info = run_query("SELECT * FROM manager JOIN manager_session ON manager_session.manager_id=manager.id WHERE token=?",[session_token])
    if manager_info is not None:
        manager_id = manager_info[0][0]
        data = request.json
        build_statement = ""
        # string join
        build_vals = []
        if data.get('username'):
            new_username = data.get('username')
            build_vals.append(new_username)
            build_statement+="username=?"
        else:
            pass
        if data.get('password'):
            new_password_input = data.get('password')
            new_password = encrypt_password(new_password_input)
            build_vals.append(new_password)
            if ("username" in build_statement):
                build_statement+=",password=?"
            else:
                build_statement+="password=?"
        else:
            pass
        if data.get('firstName'):
            new_first_name = data.get('firstName')
            build_vals.append(new_first_name)
            if ("username" in build_statement) or ("password" in build_statement):
                build_statement+=",first_name=?"
            else:
                build_statement+="first_name=?"
        else:
            pass
        if data.get('lastName'):
            new_last_name = data.get('lastName')
            build_vals.append(new_last_name)
            if ("username" in build_statement) or ("password" in build_statement) or ("first_name" in build_statement):
                build_statement+=",last_name=?"
            else:
                build_statement+="last_name=?"
        else:
            pass
        build_vals.append(manager_id)
        statement = str(build_statement)
        run_query("UPDATE manager SET "+statement+" WHERE id=?", build_vals)
        # Create error(500) for the server time out, or another server issue during the update process
        return jsonify("Your info was successfully edited"), 204
    else:
        return jsonify("Session not found"), 500

@app.delete('/api/manager')
def delete_account():
    params = request.args
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 401
    session = run_query("SELECT * FROM manager_session WHERE token=?",[session_token])
    if session is not None:
        user_id = session[0][3]
        run_query("DELETE FROM manager_session WHERE token=?",[session_token])
        run_query("DELETE FROM manager WHERE id=?",[user_id])
        return jsonify("Account deleted"), 204
    else:
        return jsonify("You must be logged in to delete your account"), 500