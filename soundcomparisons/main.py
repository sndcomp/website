# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
run this file to start the app for development
"""
from soundcomparisons import app


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
