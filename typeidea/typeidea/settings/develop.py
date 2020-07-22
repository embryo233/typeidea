from .base import * #NOQA


DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR,'db.sqlite3'),
    }
}

INSTALLED_APPS+=[
    #'debug_toolbar',
    #'pympler',
    #'debug_toolbar_line_profiler',
    'silk',
]
MIDDLEWARE+=[
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'silk.middleware.SilkyMiddleware',
]

#INTERNAL_IPS=['127.0.0.1']
INTERNAL_IPS=['192.168.11.100']

#def show_toolbar(request):
#    return True
#DEBUG_TOOLBAR_CONFIG = {
#    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
#}
DEBUG_TOOLBAR_CONFIG = {
        'JQUERY_URL' : "https://cdn.bootcdn.net/ajax/libs/jquery/3.3.1/jquery.min.js",
}
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    'djdt_flamegraph.FlamegraphPanel',        
    'pympler.panels.MemoryPanel',
    'debug_toolbar_line_profiler.panel.ProfilingPanel',

]

#DEBUG_TOOLBAR_PANELS=[
#    'djdt_flamegraph.FlamegraphPanel',        
#]
