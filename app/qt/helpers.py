def get_screen_params(app):
    screen = app.primaryScreen()
    print("### Screen Params ###")
    print("Screen: %s" % screen.name())
    size = screen.size()
    print("Size: %d x %d" % (size.width(), size.height()))
    rect = screen.availableGeometry()
    available_screen_size = rect.width(), rect.height()
    print("Available: %d x %d" % (available_screen_size[0], available_screen_size[1]))
    return available_screen_size
