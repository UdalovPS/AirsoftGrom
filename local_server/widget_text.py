class WidgetText():
    def __init__(self, lng):
        if lng == 'eng':
            self.reset = 'Clear'
            self.point_names = ('Point 1', 'Point 2', 'Point 3', 'Point 4', 'Point 5',
                                'Point 6', 'Point 7', 'Point 8', 'Point 9', 'Point 10')
            self.title = 'Grom'
            self.open_port = 'Start sending'
            self.close_port = 'Stop sending'
            self.star_read = 'Start read'
