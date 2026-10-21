from flask import render_template, request, session

from .errors import AuthError

def handle_auth_error(err: AuthError):
    """401 shows the sign-in page; 400 and 403 show the error page.
    The 401 page has a button instead of redirecting to Auth0 on its own:
    if the token were rejected by a configuration mistake, an automatic
    redirect would bounce between Flask and Auth0 forever.
    """
    if err.status_code == 401:
        session.pop("access_token", None) # expired or invalid: useless now
        return render_template("auth/signin.html", next=request.path), 401
    return render_template("auth/forbidden.html", status=err.status_code,

message=err.error["description"]), err.status_code