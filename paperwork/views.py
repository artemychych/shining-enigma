from django.http.request import HttpRequest

from django.shortcuts import render

from google_auth_oauthlib.flow import Flow


def index_page(request: HttpRequest):
    code = request.GET.get('code')
    if code:
        print('!!!', 'code', code)
    scopes = ['email', 'openid', 'profile']
    flow = Flow.from_client_secrets_file('client_secret.json', scopes)
    flow.redirect_uri = request.build_absolute_uri()
    state = '1234'
    auth_url, state = flow.authorization_url(access_type='offline', state=state)
    context = {'auth_url': auth_url}
    return render(request, 'paperwork/index.html', context=context)
