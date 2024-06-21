from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from pyvis.network import Network
import requests
import os
import base64

def LoadTopologyHTML(web_view):
    # Setting Web Engine
    settings = QWebEngineSettings.globalSettings()
    settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
    settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
    # LOAD topology.html
    with open('topology.html', 'r') as f:
        html = f.read()
        web_view.setHtml(html)

def TopologyCreat(token_info):
    # Extract topics from token_info
    sub_topics = eval(token_info['sub_topic'])
    pub_topics = eval(token_info['pub_topic'])

    # Convert the icon image to base64
    with open("icons8-jaxcore-100.png", "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Create Network graph
    net = Network(notebook=True, bgcolor="#ebedef")

    # Add device node with base64 image
    device_node = token_info['code']
    image_html = f"data:image/png;base64,{base64_image}"
    net.add_node(device_node, label=device_node, shape='image', image=image_html, title="Main Device")

    # Add subscription nodes
    for sub_topic in sub_topics:
        net.add_node(sub_topic, label=sub_topic, color="#FFA500", shape='box', title="Subscribe Topic")
        net.add_edge(device_node, sub_topic, title="subscribes to")

    # Add publication nodes
    for pub_topic in pub_topics:
        net.add_node(pub_topic, label=pub_topic, color="#00FF00", shape='box', title="Publish Topic")
        net.add_edge(pub_topic, device_node, title="publishes to")

    # Save in topology.html
    net.show("topology.html")
