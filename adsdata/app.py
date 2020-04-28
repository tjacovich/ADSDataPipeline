from adsputils import ADSCelery


class ADSDataPipelineCelery(ADSCelery):
    
    def __init__(self, app_name, *args, **kwargs):
        ADSCelery.__init__(self, app_name, *args, **kwargs)
