from __future__ import print_function
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import pandas as pd

config = "Output/config.csv"

df = pd.read_csv(config)

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template("report_template.html")

html_out = template.render(items = df)

HTML(string=html_out).write_pdf("test.pdf", stylesheets=["reportstyle.css"])
