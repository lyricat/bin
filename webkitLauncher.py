#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
'''WebkitGtk Browser Launcher
@author: Jiahua Huang <jhuangjiahua@gmail.com>
@license: LGPLv3+
@see: 
'''

VIEW_SIZE = (320, 480)

import gobject
import gtk
import pango
import webkit
import urllib
import sys
import os
import ctypes


if gtk.get_default_language().to_string() == 'zh-cn':
    i18n_zh_cn_dict = {
            '_View Source': u'查看源码(_V)',
            }
    def _(msg):
        return i18n_zh_cn_dict.get(msg, msg)
else:
    from gettext import gettext as _

TITLE = _("WebKitLauncher.py")

phantomLimbJs = '''
// Phantom Limb
// Simulate touch events in desktop browsers
// Brian Carstensen <brian.carstensen@gmail.com>

window.phantomLimb = (function() {
    debug = false;
    
    var supportsNativeTouch = 'ontouchstart' in document.createElement('button');

    // This will fake an arbitrary event on a node and add in the extra touch-related properties
    var fireTouchEvent = function(originalEvent, newType) {
        var newEvent = document.createEvent('MouseEvent');
        newEvent.initMouseEvent(newType, true, true, window, originalEvent.detail, 
        originalEvent.screenX, originalEvent.screenY, originalEvent.clientX, originalEvent.clientY, 
        originalEvent.ctrlKey, originalEvent.shiftKey, originalEvent.altKey, originalEvent.metaKey, 
        originalEvent.button, originalEvent.relatedTarget
        );

        // Touch events have a touches array, which contains kinda-sub-event objects
        // In this case we'll only need the one
        if (!('touches' in newEvent))
            newEvent.touches = newEvent.targetTouches = [newEvent];

        // And and they have "page" coordinates, which I guess are just like screen coordinates
        if (!('pageX' in newEvent))
            newEvent.pageX = originalEvent.clientX;
        if (!('pageY' in newEvent))
            newEvent.pageY = originalEvent.clientY;

        // TODO: Read the spec, fill in what's missing
        
        if (debug)
            console.log('Created simulated ' + newType + ' event', newEvent);

        // Fire off the new event
        if (debug)
            console.log('Firing simulated ' + newType + ' event', originalEvent.target);
        originalEvent.target.dispatchEvent(newEvent);
    };

    // node.ontouch* must be added as an event listener
    var convertPropped = function(node, event) {
        var handler = node['on' + event];
        if (!handler)
            return;
        
        console.info('Phantom Limb is converting an on' + event + ' event handler property to an added event listener', node);
        node.addEventListener(event, handler, false);
        
        delete node['on' + event];
    };

    // <node ontouch*="" /> must be added as an event listener
    var convertInlined = function(node, event) {
        var handler = node.getAttribute('on' + event);
        if (!handler)
            return;
        
        console.info('Phantom Limb is converting an inline ' + event + ' event handler to an added event listener', node);
        
        node.removeAttribute('on' + event);
        node.addEventListener(event, new Function('event', handler), false);
    };

    // Attach the main mouse event listeners to the document
    var attachDocTouchListeners = function() {
        // Keep track for touchmove
        var mouseIsDown = false;
        
        document.addEventListener('mousedown', function(e) {
            convertPropped(e.target, 'touchstart');
            convertInlined(e.target, 'touchstart');
            
            fireTouchEvent(e, 'touchstart');
            
            mouseIsDown = true;
        }, false);
        
        document.addEventListener('mousemove', function(e) {
            if (!mouseIsDown)
                return;
            
            convertPropped(e.target, 'touchmove');
            convertInlined(e.target, 'touchmove');
            
            fireTouchEvent(e, 'touchmove');
        }, false);
        
        document.addEventListener('mouseup', function(e) {
            convertPropped(e.target, 'touchend');
            convertInlined(e.target, 'touchend');
            
            mouseIsDown = false;
            
            fireTouchEvent(e, 'touchend');
        }, false);

    // TODO: touchcancel?
    };
    
    var pointer = document.createElement('img');
    var isPointing = false;

    // Create a cheesy finger that follows around the cursor
    // "options" includes src, x, y, and opacity
    createPointer = function(options) {
        pointer.src = options.src;
        
        pointer.style.position = 'fixed';
        pointer.style.left = '9999em';
        pointer.style.top = '9999em';
        pointer.style.zIndex = 9999;
        
        pointer.style.opacity = options.opacity;
        pointer.style.WebkitTransformOrigin = options.x + 'px ' + options.y + 'px';
        pointer.style.MozTransformOrigin = options.x + 'px ' + options.y + 'px';
        
        document.body.appendChild(pointer);
        document.documentElement.style.cursor = 'crosshair';
        
        document.addEventListener('mousemove', function(e) {
            pointer.style.left = e.clientX - options.x + 'px';
            pointer.style.top = e.clientY - options.y + 'px';
            
            var triWidth = (options.lefty ? 0 : -window.innerWidth) + e.clientX;
            var triHeight = window.innerHeight - e.clientY;
            var triHypo = Math.sqrt(Math.pow(triWidth, 2) + (Math.pow(triHeight, 2)));
            
            var angle = Math.acos(triHeight / triHypo) / (2 * Math.PI) * 360;
            angle = angle / 1.5;
            
            pointer.style.WebkitTransform = 'rotate(' + (options.lefty ? 1 : -1) * angle + 'deg) scaleX(' + (options.lefty ? -1 : 1) + ')';
            pointer.style.MozTransform = 'rotate(' + (options.lefty ? 1 : -1) * angle + 'deg) scaleX(' + (options.lefty ? -1 : 1) + ')';
        }, false);
    };
    
    return {
        init: function(options) {
            settings = {
                debug: false,
                force: false,
                src: '',
                x: 100,
                y: -7,
                opacity: 1,
            };
            
            for (var o in options || {})
                settings[o] = options[o];
            
            debug = settings.debug;
            
            if (!supportsNativeTouch || settings.force) {
                console.info('Phantom Limb will attempt to reinterpret touch events as mouse events.');
                attachDocTouchListeners();
                
                if (settings.src)
                    createPointer(settings);
            } else {
                console.log('Phantom Limb won\'t do anything because touch is supported natively.');
            }
        },

        // Show or hide the floating hand
        togglePointer: function() {
            pointer.style.display = pointer.style.display === 'none' ? '' : 'none';
        }
    };
}());

phantomLimb.init({src: "data:image;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAADklEQVQY02NgGAWDEwAAAZoAAQuinR8AAAAASUVORK5CYII=", lefty:false});
'''

USERJS = phantomLimbJs
USERJS = ''

def get_search_uri(word):
    search_url = "http://www.bing.com/search?q=%s"
    search_url = "http://www.google.com/search?q=%s"
    return search_url % urllib.quote_plus(word)

def webkit_set_proxy_uri(uri):
    ## 只支持 http、https 代理
    if uri and '://' not in uri:
        uri = 'http://' + uri
    try:
        libgobject = ctypes.CDLL('libgobject-2.0.so.0')
        libsoup = ctypes.CDLL('libsoup-2.4.so.1')
        try:
            libwebkit = ctypes.CDLL('libwebkitgtk-1.0.so.0')
        except:
            libwebkit = ctypes.CDLL('libwebkit-1.0.so.2')
        proxy_uri = libsoup.soup_uri_new(str(uri))
        session = libwebkit.webkit_get_default_session()
        session.set_property("max-conns-per-host", 1)
        libgobject.g_object_set(session, "proxy-uri", proxy_uri, None)
        libsoup.soup_uri_free(proxy_uri)
        return 0
    except:
        return 1


class Inspector (gtk.Window):
    def __init__ (self, inspector):
        """initialize the WebInspector class"""
        gtk.Window.__init__(self)
        self.set_default_size(600, 480)

        self._web_inspector = inspector

        self._web_inspector.connect("inspect-web-view",
                                    self._inspect_web_view_cb)
        self._web_inspector.connect("show-window",
                                    self._show_window_cb)
        self._web_inspector.connect("attach-window",
                                    self._attach_window_cb)
        self._web_inspector.connect("detach-window",
                                    self._detach_window_cb)
        self._web_inspector.connect("close-window",
                                    self._close_window_cb)
        self._web_inspector.connect("finished",
                                    self._finished_cb)

        self.connect("delete-event", self._close_window_cb)

    def _inspect_web_view_cb (self, inspector, web_view):
        """Called when the 'inspect' menu item is activated"""
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        webview = webkit.WebView()
        scrolled_window.add(webview)
        scrolled_window.show_all()

        self.add(scrolled_window)
        return webview

    def _show_window_cb (self, inspector):
        """Called when the inspector window should be displayed"""
        self.present()
        return True

    def _attach_window_cb (self, inspector):
        """Called when the inspector should displayed in the same
        window as the WebView being inspected
        """
        return False

    def _detach_window_cb (self, inspector):
        """Called when the inspector should appear in a separate window"""
        return False

    def _close_window_cb (self, inspector, view=None):
        """Called when the inspector window should be closed"""
        self.hide()
        return True

    def _finished_cb (self, inspector):
        """Called when inspection is done"""
        self._web_inspector = 0
        self.destroy()
        return False


class WebView(webkit.WebView):
    def __init__(self):
        webkit.WebView.__init__(self)
        settings = self.get_settings()
        settings.set_property("enable-developer-extras", True)
        settings.set_property("enable-spell-checking", True)

        settings = self.get_settings()
        settings.set_property('enable-universal-access-from-file-uris', True)
        settings.set_property('javascript-can-access-clipboard', True)
        settings.set_property('enable-default-context-menu', True)
        settings.set_property('enable-page-cache', True)
        settings.set_property('tab-key-cycles-through-elements', True)
        settings.set_property('enable-file-access-from-file-uris', True)
        settings.set_property('user-agent', 'Mozilla/5.0 (iPhone; U; Linux; zh-cn) AppleWebKit/532+ (KHTML, like Gecko) Version/3.0 Mobile/1A538b Safari/419.3')
        #settings.set_property('user-agent', 'Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; MB525 Build/3.4.2-155) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1')

        # scale other content besides from text as well
        self.set_full_content_zoom(True)

        # make sure the items will be added in the end
        # hence the reason for the connect_after
        self.connect_after("populate-popup", self.populate_popup)
        ##
        self.connect_after("hovering-over-link", self.on_over_link)

    def on_over_link(self, view, alt, href):
        gobject.idle_add(self.parent.set_tooltip_text, ((alt + '\n' + href) if alt else href))

    def populate_popup(self, view, menu):
        is_normal =  len(menu.get_children()) < 10
        menu.append(gtk.SeparatorMenuItem())
        # zoom buttons
        zoom_in = gtk.ImageMenuItem(gtk.STOCK_ZOOM_IN)
        zoom_in.connect('activate', self.zoom_in_cb, view)
        menu.append(zoom_in)
        zoom_in.show()

        zoom_out = gtk.ImageMenuItem(gtk.STOCK_ZOOM_OUT)
        zoom_out.connect('activate', self.zoom_out_cb, view)
        menu.append(zoom_out)
        zoom_out.show()

        zoom_hundred = gtk.ImageMenuItem(gtk.STOCK_ZOOM_100)
        zoom_hundred.connect('activate', self.zoom_hundred_cb, view)
        menu.append(zoom_hundred)
        zoom_hundred.show()

        menu.append(gtk.SeparatorMenuItem())

        editableitem = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        editableitem.connect('activate', self.on_editable)
        menu.append(editableitem)
        editableitem.show()

        printitem = gtk.ImageMenuItem(gtk.STOCK_PRINT)
        menu.append(printitem)
        printitem.connect('activate', self.print_cb, view)
        printitem.show()

        view_source = gtk.ImageMenuItem(gtk.STOCK_JUSTIFY_RIGHT)
        view_source.set_label(_("_View Source"))
        menu.append(view_source)
        view_source.connect('activate', self.view_source_mode_requested_cb)
        view_source.show()

        page_properties = gtk.ImageMenuItem(gtk.STOCK_PROPERTIES)
        menu.append(page_properties)
        page_properties.connect('activate', self.page_properties_cb, view)
        page_properties.show()

        menu.show_all()
        ##
        if self.get_pointer()[1] < 0:
            newwindow = gtk.ImageMenuItem(gtk.STOCK_NEW)
            newwindow.connect('activate', self.on_new)
            menu.insert(newwindow, 0)
            newwindow.show()
            separator = gtk.SeparatorMenuItem()
            menu.insert(separator, 1)
            separator.show()
            menu.hide()
            x, y, s = gtk.gdk.get_default_root_window().get_pointer()
            def func(*args):
                return (x, y, 100)
            gobject.idle_add(menu.popup, None, None, func, 0, 0)
            return True
        return False

    def on_editable(self, *args):
        self.set_editable(not self.get_editable())
        pass

    def on_new(self, *args):
        BrowserWindow()
        pass

    def page_properties_cb(self, menu_item, web_view):
        title = _("Properties")
        parent = None
        dlg = gtk.Dialog(title, parent, gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_OK),
            )
        vbox = dlg.vbox
        mainframe = self.get_main_frame()
        datasource = mainframe.get_data_source()
        main_resource = datasource.get_main_resource()
        ##
        info = [
                [_("MIME Type:"), main_resource.get_mime_type()],
                [_("URI: "), main_resource.get_uri()],
                [_("Encoding: "), main_resource.get_encoding()],
        ]
        ##
        table = gtk.Table()
        y = 0
        for line in info:
            x = 0
            left = 0
            for text in line:
                label = gtk.Label()
                #label.set_selectable(1) # 会干扰编辑区选中状态
                label.set_padding(10, 3)
                label.set_alignment(left, 0)
                label.set_markup("%s" % text)
                label.show()
                table.attach(label, x, x+1, y, y+1,)
                x += 1
                left = 1
                pass
            y += 1
            pass
        dlg.vbox.pack_start(table, False, False, 5)
        ##
        dlg.show_all()
        dlg.connect('response', self._widget_destroy)
        dlg.connect('close', self._widget_destroy)
        pass

    def _widget_destroy(self, widget, *args):
        widget.destroy()
        pass

    def view_source_mode_requested_cb(self, *args):
        self.set_view_source_mode(not self.get_view_source_mode())
        self.reload()
        pass

    def zoom_in_cb(self, menu_item, web_view):
        """Zoom into the page"""
        web_view.zoom_in()
        pass
    
    def zoom_out_cb(self, menu_item, web_view):
        """Zoom out of the page"""
        web_view.zoom_out()
        pass
    
    def zoom_hundred_cb(self, menu_item, web_view):
        """Zoom 100%"""
        if not (web_view.get_zoom_level() == 1.0):
            web_view.set_zoom_level(1.0)
            pass
        pass

    def print_cb(self, menu_item, web_view):
        mainframe = web_view.get_main_frame()
        mainframe.print_full(gtk.PrintOperation(), gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG)
        pass

_windows = []

class BrowserWindow(gtk.Window):
    def __init__(self, url="", webview=None, show_progress=False):
        global _windows
        gtk.Window.__init__(self)
        _windows.append(self)
        self.set_default_size(800, 600)
        self.connect('destroy', self.destroy_cb)
        ##
        vbox = gtk.VBox(spacing=1)
        ##
        toolbar = gtk.Toolbar()
        ## Back, Forward Button
        backButton = gtk.ToolButton(gtk.STOCK_GO_BACK)
        backButton.connect('clicked', self.go_back)
        backButton.show()
        toolbar.insert(backButton, -1)
        forwardButton = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        forwardButton.connect('clicked', self.go_forward)
        forwardButton.show()
        toolbar.insert(forwardButton, -1)
        ## Url Entry
        self.url_entry = gtk.Entry()
        self.url_entry.connect('activate', self._entry_activate_cb)
        entry_item = gtk.ToolItem()
        entry_item.set_size_request(0, 0)
        entry_item.set_expand(True)
        entry_item.add(self.url_entry)
        self.url_entry.show()
        toolbar.insert(entry_item, -1)
        entry_item.show()
        ##
        toolButton = gtk.ToolButton(gtk.STOCK_PREFERENCES)
        toolButton.connect('clicked', self.do_popup_menu)
        toolButton.show()
        toolbar.insert(toolButton, -1)
        ##
        vbox.pack_start(toolbar, expand=False, fill=False)
        ##
        if webview:
            self.webview = webview
            pass
        else:
            self.webview = WebView()
            pass
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        scrolled_window.add(self.webview)
        vbox.pack_start(scrolled_window)
        ##
        scrolled_window.set_size_request(*VIEW_SIZE)
        self.resize(*VIEW_SIZE)
        gobject.timeout_add(100, scrolled_window.set_size_request, 0, 0)
        ##
        self.inspector = Inspector(self.webview.get_web_inspector())
        self.inspector.parentwindow = self
        self.webview.connect("title-changed", self._title_changed_cb)
        self.webview.connect("load-finished", self._load_finished_cb)
        self.webview.connect("create-web-view", self.on_create_web_view)
        if show_progress:
            self.webview.connect("load-progress-changed", self._load_progress_changed)
            pass
        if url:
            self.open(url)
            pass
        self.add(vbox)
        self.show_all()
        pass

    def go_back(self, *args):
        self.webview.go_back()
        pass

    def go_forward(self, *args):
        self.webview.go_forward()
        pass

    def do_popup_menu(self, *args):
        self.webview.do_popup_menu(self.webview)
        pass

    def on_create_web_view(self, webview, webframe):
        window = BrowserWindow()
        webview = window.webview
        webview.connect("web-view-ready", self.on_web_view_ready_cb)
        return webview
        pass

    def on_web_view_ready_cb(self, webview):
        window = webview.get_toplevel()
        window.show_all()
        pass

    def destroy_cb(self, *args):
        global _windows
        _windows.remove(self)
        if not _windows:
            gtk.main_quit()
            pass
        pass

    def _load_progress_changed(self, webview, progress):
        frame = webview.get_main_frame()
        title = frame.get_title()
        if progress == 100:
            self.set_title("%s - %s" % (title, TITLE))
            pass
        else:
            self.set_title("%s - %s (%s/100%%)" % (title, TITLE, progress))
            pass
        pass

    def _load_finished_cb(self, view, frame, *args):
        if USERJS:
            view.execute_script(USERJS)
            pass
        url = frame.get_uri()
        if url == "about:blank":
            url = ""
            gobject.idle_add(self.url_entry.grab_focus)
            pass
        self.url_entry.set_text(url)
        pass

    def _title_changed_cb(self, view, frame, title=""):
        url = frame.get_uri()
        title = frame.get_title()
        if not title and url == "about:blank":
            gobject.idle_add(self.url_entry.grab_focus)
            pass
        else:
            gobject.idle_add(self.webview.grab_focus)
            pass
        if not title:
            title = url
            pass
        if title == "about:blank":
            self.set_title(TITLE)
            pass
        else:
            self.set_title("%s - %s" % (title, TITLE))
            pass
        self.inspector.set_title("%s - %s" % (_("Inspector"), url))
        if url == "about:blank":
            url = ""
            pass
        self.url_entry.set_text(url)
        pass

    def _entry_activate_cb(self, *args):
        url = self.url_entry.get_text()
        self.open(url)

    def open(self, url):
        text = url
        if not text:
            return
        if text.startswith('javascript:'):
            text = urllib.unquote(text[11:])
            gobject.idle_add(self.webview.execute_script, text)
            return
        elif "://" not in text and not text.startswith("about:"):
            if text.startswith("g ") or text.startswith(" "):
                text = get_search_uri(text[1:])
                pass
            elif "." in text:
                text = "http://" + text
                pass
            else:
                text = get_search_uri(text)
                pass
        gobject.idle_add(self.webview.open, text)
        pass

def main():
    gobject.threads_init()
    gtk.window_set_default_icon_name(gtk.STOCK_FILE)
    settings = gtk.settings_get_default()
    settings.props.gtk_toolbar_style = gtk.TOOLBAR_ICONS
    settings.props.gtk_toolbar_icon_size = gtk.ICON_SIZE_SMALL_TOOLBAR
    ## proxy settings
    proxies = urllib.getproxies()
    if 'http' in proxies:
        webkit_set_proxy_uri(proxies['http'])
    elif 'https' in proxies:
        webkit_set_proxy_uri(proxies['https'])
    ##
    if sys.argv[1:]:
        url = sys.argv[1]
        if os.path.exists(url):
            url = 'file://' + os.path.abspath(url)
        webbrowser = BrowserWindow(url)
    else:
        webbrowser = BrowserWindow(url = 'about:blank')
    gtk.main()
    pass
    
if __name__ == "__main__":
    main()
    pass
