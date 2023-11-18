from ..models import Settings

blue_css = """/* Theme Blue*/
    palette {background: rgb(17, 133, 209, 255); disabled: rgb(200, 200, 200, 255);}
    QMainWindow {icon-size: 28px, 28px; background: #118CED}
    QDialog {border: none; background: rgb(17, 133, 209, 255);}
    QToolBar {
        border: none;
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgb(0, 75, 165, 255),
        stop: 0.05 rgb(31, 164, 227, 255),
        stop: 0.5 rgb(17, 133, 209, 255),
        stop: 0.95 rgb(0, 102, 185, 255),
        stop: 1 rgb(0, 75, 165, 255));
        background: rgb(17, 133, 209, 255);
        min-height: 50px;
    }
    QToolButton {
        border: none;
        border-style: flat;
        color: white;
        font: bold 10ft;
        min-height: 50px;
        min-width: 50px;}
    QPushButton:hover, QPushButton:pressed, QToolButton:hover, QToolButton:pressed {
        background-color: rgb(238, 178, 17, 200);}
    QPushButton:checked, QToolButton:checked {
        background-color: rgb(255, 255, 255, 50);}
    QPushButton {
        padding: 3px;
        border: none;
        border-style: flat;
        border-radius: 4px;
        color: white;
        background-color: rgb(255, 255, 255, 50);
        font: bold 10ft;
        min-height: 20px;
        min-width: 20px;}
    /* >>> QToolBar: QLineEdit/QComboBox */
    QLineEdit, QComboBox:!editable, QSpinBox {
        border: none;
        border-radius: 4px;
        background-color: white;
        padding: 3px;
        min-height: 20px;}
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {
        background-color: rgb(200, 200, 200, 255);}
    QComboBox:!editable {
        padding-right: 5px;}
    /* QComboBox gets the "on" state when the popup is open */
    QComboBox:!editable:on, QToolBar > QComboBox::drop-down:editable:on {
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #D3D3D3, stop: 0.4 #D8D8D8, stop: 0.5 #DDDDDD, stop: 1.0 #E1E1E1);}
    QComboBox:on {padding-top: 3px; padding-left: 4px;}
    QComboBox::drop-down {
     subcontrol-origin: padding;
     subcontrol-position: top right;
     width: 20px;
     border-left-width: 0px;
     border-top-right-radius: 4px; /* same radius as the QComboBox */
     border-bottom-right-radius: 4px;
    }
    QComboBox::down-arrow {image: url(:/icons/down-arrow.png);}
    QComboBox::down-arrow:disabled {image: none;}
    QComboBox::down-arrow:on { /* shift the arrow when popup is open */
     top: 1px; left: 1px;}
    /* <<< QToolBar: QLineEdit/QComboBox */
    /* >>> QDockWidget */
    QDockWidget {
        margin: 0px;
        background-color: rgb(17, 133, 209,  255);
        border: 0px; padding: 0px;
        color: rgb(17, 133, 209,  255);
        font-size: 15px; font-weight: bold;
    }
    QDockWidget::title  {
        margin: 0px;
        text-align: left center;
        background-color: rgb(255, 255, 255, 255);
        border: 0px;
        color: white;
        padding: 8px;
    }
    QDockWidget > QWidget{
        margin: 0px;
        background-color: rgb(17, 133, 209,  255);
        border: 0px;
        padding: 0px;
    }
    QScrollArea #measureWidget, QScrollArea #dsoTriggerWidget, QScrollArea #triggerWidget, QScrollArea #protocolWidget{
        margin: 0px;
        background-color: rgb(17, 133, 209,  255);
        border: 0px;
        padding: 0px;
    }
    QGroupBox:disabled {
        color: rgb(200, 200, 200, 255);
    }
    #triggerWidget > QTabWidget::pane{
        margin: 0px;background-color: rgb(17, 133, 209,  255);
        border: 1px solid rgb(255, 255, 255); padding: 0px;
    }
    #triggerWidget > QTabWidget::pane:disabled{
        border: 1px solid rgb(200, 200, 200, 255);
    }
    QTabWidget::pane{
        margin: 0px; background-color: rgb(17, 133, 209,  255);
        border: 0px solid rgb(255, 255, 255); padding: 0px;
    }
    QCheckBox, QRadioButton, QLabel {border: none; min-height: 20px;}
    QCheckBox::checked, QRadioButton::checked {color: black;}
    QLabel, QCheckBox::unchecked, QRadioButton::unchecked {color: white;}
    QCheckBox, QLabel {padding: 1px 1px 1px 1px; margin: 0px;}
    QLabel:disabled {color: rgb(200, 200, 200, 255);}
    QSlider::groove:horizontal {
        border: 1px solid #999999; height: 2px; margin: 0px 0; left: 10px;
        right: 10px; border-radius: 4px;}
    QSlider::handle:horizontal { margin-left: -12px;
        margin-right: -12px; margin-top: -11px; margin-bottom: -11px;
    }
    QSlider::sub-page:horizontal{
        background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0,
            stop:0 rgba(17, 133, 209,  255), stop:0.25 rgba(238, 178, 17, 255),
            stop:0.75 rgba(238, 178, 17, 255),
            stop:1 rgba(17, 133, 209,  255)); height: 2px; border-radius: 4px;
    }
    QSlider::add-page:horizontal{
        background: qlineargradient(spread:pad,
            x1:0, y1:1, x2:0, y2:0, stop:0 rgba(17, 133, 209,  255),
            stop:0.25 rgba(255, 255, 255, 255), stop:0.75 rgba(255, 255, 255, 255),
            stop:1 rgba(17, 133, 209,  255)); height: 2px; border-radius: 4px;
        }
    QGroupBox {
        background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #669cf2, stop: 1 #78c7f5); border: 2px solid #FFF;
        border-radius: 5px; font: bold 30px; margin-top: 8ex; /* leave space at the top for the title */
    }
    QGroupBox > QLabel {
    color: #000;
    }
    QGroupBox::title {
    color: #000;
        border-top: 2px solid #FFF;
        subcontrol-position: top center; padding: 0 3px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #669cf2, stop: 1 #FFFFFF);
        subcontrol-origin: margin;
        subcontrol-position: top center;
        border-top-right-radius: 15px; border-top-left-radius: 15px;
        padding: 15px 50px; background-color: #669cf2;
    }
    QTableWidget::item {
        border: 1px solid #FFF;border-radius: 1px;background-color: #669cf2;}
        QTableView{border: 1px solid #78879b;gridline-color: #78879b;background-color: #3d8ec9;color: #FFFFFF;}
        QTableView, QHeaderView{border-radius: 1px;color: #FFFFFF;}
        QTableView::item:pressed, QListView::item:pressed, QTreeView::item:pressed  {background: #78879b;color: #FFFFFF;}
        QTableView::item:selected:active, QTreeView::item:selected:active, QListView::item:selected:active  {background: #3d8ec9;color: #FFFFFF;}
        QTableCornerButton::section {background-color: #669cf2;border: 1px solid #669cf2;border-radius: 2px;}
        QTableWidget::item {color: #000;/*border-bottom: 1px solid #669cf2;background-color: #669cf2;*/}
        QToolTip{border: 1px solid #FFF;background-color: rgb(90, 102, 117);color: white;padding: 1px;opacity: 200;
    }
    """
drak_ccs = """/* Theme Drak */
    QProgressBar:horizontal {border: 1px solid #3A3939;text-align: center;padding: 1px;background: #201F1F;}
    QProgressBar::chunk:horizontal {background-color: qlineargradient(spread:reflect, x1:1, y1:0.545, x2:1, y2:0, stop:0 rgba(28, 66, 111, 255), stop:1 rgba(37, 87, 146, 255));}
    QHeaderView{border: 1px transparent;margin: 0px;padding: 0px;}
    QHeaderView::section{background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:1, y2:0, stop:0 #3A3A3A, stop:1 #bbb);
        color: white;border-radius:0px;padding: 4px;border: 1px solid #6c6c6c;text-align: center;text-transform: uppercase;font:bold}
    QHeaderView::section::vertical::first, QHeaderView::section::vertical::only-one {border-top: 1px solid #6c6c6c;}
    QHeaderView::section::vertical{border-top: transparent;}
    QHeaderView::section::horizontal::first, QHeaderView::section::horizontal::only-one {border-left: 1px solid #6c6c6c;}
    QHeaderView::section::horizontal{border-left: transparent;}
    QHeaderView::section:checked{color: white;background-color: #5A5959;}
    /* style the sort indicator */
    /*TABLE*/
    QTableWidget::item:hover {border: 1px solid #bbb;border-radius: 1px;background-color: #3A3A3A;}
    QTableView{border: 3px solid #444;gridline-color: #FFFFFF;background-color: #4A4949;color: #FFFFFF;}
    QTableView, QHeaderView{border-radius: 1px;color: #FFFFFF;}
    QTableView::item:pressed, QListView::item:pressed, QTreeView::item:pressed  {background: #78879b;color: #FFFFFF;}
    QTableView::item:selected:active, QTreeView::item:selected:active, QListView::item:selected:active  {background: #48576b;color: #FFFFFF;}
    QTableCornerButton::section {background-color: #3A3939;border: 1px solid #3A3939;border-radius: 2px;}
    QTableWidget::item {color: white;border-bottom: 1px solid #3A3A3A;background-color: #3A3A3A;}
    QToolTip{border: 1px solid #3A3939;background-color: rgb(90, 102, 117);color: white;padding: 1px;opacity: 200;}
    QWidget{color: silver;background-color: #302F2F;selection-background-color:#48576b;selection-color: black;background-clip: border;/*    border-image: none;*/outline: 0;}
    QWidget:item:hover{background-color: #78879b;color: #3A3A3A;}
    QWidget:item:selected{background-color: #48576b;}
    QCheckBox{spacing: 5px;outline: none; color: #bbb;margin-bottom: 2px;}
    QCheckBox:disabled{color: #777777;}
    QCheckBox::indicator, QGroupBox::indicator{width: 18px;height: 18px;}
    QGroupBox::indicator{margin-left: 2px;}
    QCheckBox::indicator:checked:focus,QCheckBox::indicator:checked:pressed,
    QRadioButton{spacing: 5px;outline: none;color: #bbb;margin-bottom: 2px;}
    QRadioButton:disabled{color: #777777;}
    QRadioButton::indicator{width: 21px;height: 21px;}
    QRadioButton::indicator:unchecked:focus,QRadioButton::indicator:unchecked:pressed{border: none;outline: none;/*    image: url(:/radio_unchecked_focus.png);*/}
    QRadioButton::indicator:checked,QRadioButton::indicator:checked:hover{border: none;outline: none;/*    image: url(:/radio_checked.png);*/}
    QRadioButton::indicator:checked:focus,QRadioButton::indicato::menu-arrowr:checked:pressed{border: none;outline: none;/*    image: url(:/radio_checked_focus.png);*/}
    QRadioButton::indicator:indeterminate,QRadioButton::indicator:indeterminate:hover,QRadioButton::indicator:indeterminate:pressed{/*        image: url(:/radio_indeterminate.png);*/}
    QMenuBar{background-color: #302F2F;color: silver;}
    QMenuBar::item{background: transparent;}
    QMenuBar::item:selected {background: transparent;border: 1px solid #3A3939;}
    QMenuBar::item:pressed {border: 1px solid #3A3939;background-color: #48576b;
                            color: black;margin-bottom:-1px;padding-bottom:1px;}
    QMenu{border: 1px solid #3A3939;color: silver;margin: 2px;}
    QMenu::icon{margin: 5px;}
    QMenu::item{padding: 5px 30px 5px 30px;margin-left: 5px;border: 1px solid transparent; /* reserve space for selection border */}
    QMenu::item:selected{color: black;}
    QMenu::separator {height: 2px;background: lightblue;margin-left: 10px;margin-right: 5px}
    QMenu::indicator {width: 18px;height: 18px;}
    /* non-exclusive indicator = check box style indicator   (see QActionGroup::setExclusive) */
    QMenu::indicator:non-exclusive:unchecked {/*    image: url(:/checkbox_unchecked.png);*/}
    QMenu::indicator:non-exclusive:unchecked:selected {/*    image: url(:/checkbox_unchecked_disabled.png);*/}
    QMenu::indicator:non-exclusive:checked {/*    image: url(:/checkbox_checked.png);*/}
    QMenu::indicator:non-exclusive:checked:selected {/*    image: url(:/checkbox_checked_disabled.png);*/}
    /* exclusive indicator = radio button style indicator (see QActionGroup::setExclusive) */QMenu::indicator:exclusive:unchecked {
    /*    image: url(:/radio_unchecked.png);*/}
    QMenu::indicator:exclusive:unchecked:selected {/*    image: url(:/radio_unchecked_disabled.png);*/}
    QMenu::indicator:exclusive:checked {/*    image: url(:/radio_checked.png);*/}
    QMenu::indicator:exclusive:checked:selected {/*    image: url(:/radio_checked_disabled.png);*/}
    QMenu::right-arrow {margin: 5px;/*    image: url(:/right_arrow.png)*/}
    QWidget:disabled{color: #404040;background-color: #302F2F;}
    QAbstractItemView{alternate-background-color: #3A3939;color: silver;border: 1px solid 3A3939;border-radius: 0px;padding: 1px;}
    QWidget:focus, QMenuBar:focus{border: 1px solid #78879b;}
    QTabWidget:focus, QCheckBox:focus, QRadioButton:focus, QSlider:focus{border: none;}
    QLineEdit{background-color: #201F1F;padding: 2px;border-style: solid; border: 1px solid #3A3939;border-radius: 2px;color: silver;}QGroupBox {border:1px solid #3A3939;border-radius: 2px;margin-top: 20px;}
    QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding-left: 10px;padding-right: 10px;padding-top: 10px;}
    QAbstractScrollArea{border-radius: 2px;border: 1px solid #3A3939;background-color: transparent;}
    QScrollBar:horizontal{height: 15px;margin: 3px 15px 3px 15px;border: 1px transparent #2A2929;border-radius: 4px;background-color: #2A2929;}
    QScrollBar::handle:horizontal{background-color: #605F5F;min-width: 5px;border-radius: 4px;}
    QScrollBar::add-line:horizontal{margin: 0px 3px 0px 3px;
    /*    border-image: url(:/right_arrow_disabled.png);*/width: 10px;height: 10px;subcontrol-position: right;subcontrol-origin: margin;}
    QScrollBar::sub-line:horizontal{margin: 0px 3px 0px 3px;
    /*    border-image: url(:/left_arrow_disabled.png);*/height: 10px;width: 10px;subcontrol-position: left;subcontrol-origin: margin;}
    QScrollBar::add-line:horizontal:hover,QScrollBar::add-line:horizontal:on{
    /*    border-image: url(:/right_arrow.png);*/height: 10px;width: 10px;subcontrol-position: right;subcontrol-origin: margin;}
    QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on{
    /*    border-image: url(:/left_arrow.png);*/height: 10px;width: 10px;subcontrol-position: left;subcontrol-origin: margin;}
    QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal{background: none;}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal{background: none;}
    QScrollBar:vertical{background-color: #2A2929;width: 15px;margin: 15px 3px 15px 3px;border: 1px transparent #2A2929;border-radius: 4px;}
    QScrollBar::handle:vertical{background-color: #605F5F;min-height: 5px;border-radius: 2px;}
    QScrollBar::sub-line:vertical{margin: 3px 0px 3px 0px;
    /*    border-image: url(:/up_arrow_disabled.png);*/height: 10px;width: 10px;subcontrol-position: top;subcontrol-origin: margin;}
    QScrollBar::add-line:vertical{margin: 3px 0px 3px 0px;
    /*    border-image: url(:/down_arrow_disabled.png);*/height: 10px;width: 10px;subcontrol-position: bottom;subcontrol-origin: margin;}
    QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on {
        /*    border-image: url(:/up_arrow.png);*/height: 10px;width: 10px;subcontrol-position: top;subcontrol-origin: margin;}
    QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on {
    /*    border-image: url(:/down_arrow.png);*/height: 10px;width: 10px;subcontrol-position: bottom;subcontrol-origin: margin;}
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical{background: none;}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{background: none;}
    QTextEdit {background-color: #201F1F;color: #FFF;border: 1px solid #3A3939;}
    QTextEdit:hover { background-color: #787876; color: #FFF}
    QPlainTextEdit{background-color: #201F1F;color: #FFF;border-radius: 2px;border: 1px solid #3A3939;}
    QSizeGrip {/*    image: url(:/sizegrip.png);*/width: 12px;height: 12px;}
    QMainWindow::separator {background-color: #302F2F;color: white;padding-left: 4px;spacing: 2px;border: 1px dashed #3A3939;}
    QMainWindow::separator:hover{background-color: #787876;color: white;padding-left: 4px;border: 1px solid #3A3939;spacing: 2px;}
    QMenu::separator{height: 1px;background-color: #3A3939;color: white;padding-left: 4px;margin-left: 10px;margin-right: 5px;}
    QFrame {border-radius: 2px;border: 1px solid #444;}
    QFrame[frameShape="0"]{border-radius: 2px;border: 1px transparent #444;}
    QStackedWidget{border: 1px transparent black;}QToolBar {border: 1px transparent #393838;background: 1px solid #302F2F;font-weight: bold;}
    QToolBar::handle:horizontal {/*    image: url(:/Hmovetoolbar.png);*/}
    QToolBar::handle:vertical {/*    image: url(:/Vmovetoolbar.png);*/}
    QToolBar::separator:horizontal {/*    image: url(:/Hsepartoolbar.png);*/}
    QToolBar::separator:vertical {/*    image: url(:/Vsepartoolbars.png);*/}
    QComboBox{selection-background-color: #48576b;background-color: #201F1F;border-style: solid;border: 1px solid #3A3939;border-radius: 2px;padding: 2px;min-width: 75px;}QPushButton:checked{background-color: #4A4949;border-color: #6A6969;}
    QComboBox:hover,QAbstractSpinBox:hover,QLineEdit:hover,QPlainTextEdit:hover,QAbstractView:hover,QTreeView:hover{border: 1px solid #78879b;color: #FFF;}
    QComboBox:on{background-color: #626873;padding-top: 3px;padding-left: 4px;selection-background-color: #4a4a4a;}
    QComboBox QAbstractItemView{background-color: #201F1F;border-radius: 2px;border: 1px solid #444;selection-background-color: #3d8ec9;}
    QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: top right;width: 15px;
    border-left-width: 0px;border-left-color: darkgray;border-left-style: solid;border-top-right-radius: 3px;border-bottom-right-radius: 3px;}
    QComboBox::down-arrow{/*    image: url(:/down_arrow_disabled.png);*/}
    QComboBox::down-arrow:on, QComboBox::down-arrow:hover,QComboBox::down-arrow:focus {/*    image: url(:/down_arrow.png);*/}
    QPushButton:hover {background-color: #48576b; color: #FFF}
    QPushButton::menu-indicator  {subcontrol-origin: padding;subcontrol-position: bottom right;left: 8px;}
    QPushButton{color: #FFF;background-color: silver;border-width: 1px;border-color: gray;border-style: solid;padding-top: 5px;padding-bottom: 5px;padding-left: 5px;padding-right: 5px;border-radius: 2px;outline: none;}
    QPushButton:disabled{background-color: #302F2F;border-width: 1px;border-color: #3A3939;border-style: solid;padding-top: 5px;padding-bottom: 5px;padding-left: 10px;padding-right: 10px;/*border-radius: 2px;*/color: #454545;}QPushButton:focus {background-color: #3d8ec9;color: white;}
    QPushButton:pressed{background-color: #484846;}QAbstractSpinBox {padding-top: 2px;padding-bottom: 2px;border: 1px solid #3A3939;background-color: #201F1F;color: silver;border-radius: 2px;min-width: 75px;}
    QAbstractSpinBox:up-button{background-color: transparent;subcontrol-origin: border;subcontrol-position: center right;}
    QAbstractSpinBox:down-button{background-color: transparent;subcontrol-origin: border;subcontrol-position: center left;}
    QAbstractSpinBox::up-arrow,QAbstractSpinBox::up-arrow:disabled,QAbstractSpinBox::up-arrow:off {/*    image: url(:/up_arrow_disabled.png);*/width: 10px;height: 10px;}
    QAbstractSpinBox::up-arrow:hover{/*    image: url(:/up_arrow.png);*/}
    QAbstractSpinBox::down-arrow,QAbstractSpinBox::down-arrow:disabled,QAbstractSpinBox::down-arrow:off{
    /*    image: url(:/down_arrow_disabled.png);*/width: 10px;height: 10px;}
    QAbstractSpinBox::down-arrow:hover {/*    image: url(:/down_arrow.png);*/}
    QLabel{border: 0px solid black;color: #b1b1b1;background-color: transparent;}
    QTabWidget{border: 1px transparent black;color: white;}
    QTabWidget::pane {color: #b1b1b1;border: 1px solid #444;border-radius: 3px;padding: 3px;}
    QTabBar{qproperty-drawBase: 0;left: 5px; /* move to the right by 5px */}
    QTabBar:focus{border: 0px transparent black;}
    QTabBar::close-button  {/*    image: url(:/close.png);*/background: transparent;}
    QTabBar::close-button:hover{/*    image: url(:/close-hover.png);*/background: transparent;}
    QTabBar::close-button:pressed {/*    image: url(:/close-pressed.png);*/background: transparent;}
    /* TOP TABS */QTabBar::tab:top {color: #b1b1b1;border: 1px solid #4A4949;border-bottom: 1px transparent black;background-color: #302F2F;padding: 5px;border-top-left-radius: 2px;border-top-right-radius: 2px;}
    QTabBar::tab:top:!selected{color: #b1b1b1;background-color: #201F1F;border: 1px transparent #4A4949;border-bottom: 1px transparent #4A4949;border-top-left-radius: 0px;border-top-right-radius: 0px;}QTabBar::tab:top:!selected:hover {background-color: #48576b;}
    /* BOTTOM TABS */QTabBar::tab:bottom {color: #b1b1b1;border: 1px solid #4A4949;border-top: 1px transparent black;background-color: #302F2F;padding: 5px;border-bottom-left-radius: 2px;border-bottom-right-radius: 2px;}
    QTabBar::tab:bottom:!selected{color: #b1b1b1;background-color: #201F1F;border: 1px transparent #4A4949;border-top: 1px transparent #4A4949;border-bottom-left-radius: 0px;border-bottom-right-radius: 0px;}QTabBar::tab:bottom:!selected:hover {background-color: #78879b;}
    /* LEFT TABS */QTabBar::tab:left {color: #b1b1b1;border: 1px solid #4A4949;border-left: 1px transparent black;background-color: #302F2F;padding: 5px;border-top-right-radius: 2px;border-bottom-right-radius: 2px;}
    QTabBar::tab:left:!selected{color: #b1b1b1;background-color: #201F1F;border: 1px transparent #4A4949;border-right: 1px transparent #4A4949;border-top-right-radius: 0px;border-bottom-right-radius: 0px;}
    QTabBar::tab:left:!selected:hover {background-color: #48576b;}/* RIGHT TABS */
    QTabBar::tab:right {color: #b1b1b1;border: 1px solid #4A4949;border-right: 1px transparent black;background-color: #302F2F;padding: 5px;border-top-left-radius: 2px;border-bottom-left-radius: 2px;}
    QTabBar::tab:right:!selected{color: #b1b1b1;background-color: #201F1F;border: 1px transparent #4A4949;border-right: 1px transparent #4A4949;border-top-left-radius: 0px;border-bottom-left-radius: 0px;}QTabBar::tab:right:!selected:hover {background-color: #48576b;}
    QTabBar QToolButton::right-arrow:enabled {/*     image: url(:/right_arrow.png);*/ }
    QTabBar QToolButton::left-arrow:enabled {/*     image: url(:/left_arrow.png);*/ }
    QTabBar QToolButton::right-arrow:disabled {/*     image: url(:/right_arrow_disabled.png);*/ }
    QTabBar QToolButton::left-arrow:disabled {/*     image: url(:/left_arrow_disabled.png);*/}
    QDockWidget {border: 1px solid #403F3F;titlebar-close-icon: url(:/close.png);titlebar-normal-icon: url(:/undock.png);}QDockWidget::close-button, QDockWidget::float-button {border: 1px solid transparent;border-radius: 2px;background: transparent;}QDockWidget::close-button:hover, QDockWidget::float-button:hover {background: rgba(255, 255, 255, 10);}QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {padding: 1px -1px -1px 1px;background: rgba(255, 255, 255, 10);}
    QTreeView, QListView{border: 1px solid #444;background-color: #201F1F;}
    QTreeView:branch:selected, QTreeView:branch:hover{background: url(:/transparent.png);}
    QTreeView::branch:has-siblings:!adjoins-item {/*    border-image: url(:/transparent.png);*/}
    QTreeView::branch:has-siblings:adjoins-item {/*    border-image: url(:/transparent.png);*/}
    QTreeView::branch:!has-children:!has-siblings:adjoins-item {/*    border-image: url(:/transparent.png);*/}
    QTreeView::branch:has-children:!has-siblings:closed,QTreeView::branch:closed:has-children:has-siblings {/*    image: url(:/branch_closed.png);*/}
    QTreeView::branch:open:has-children:!has-siblings,QTreeView::branch:open:has-children:has-siblings  {/*    image: url(:/branch_open.png);*/}
    QTreeView::branch:has-children:!has-siblings:closed:hover,QTreeView::branch:closed:has-children:has-siblings:hover {/*    image: url(:/branch_closed-on.png);*/}
    QTreeView::branch:open:has-children:!has-siblings:hover,QTreeView::branch:open:has-children:has-siblings:hover  {/*    image: url(:/branch_open-on.png);*/}QListView::item:!selected:hover, QListView::item:!selected:hover, QTreeView::item:!selected:hover  {background: rgba(0, 0, 0, 0);outline: 0;color: #FFFFFF}QListView::item:selected:hover, QListView::item:selected:hover, QTreeView::item:selected:hover  {background: #3d8ec9;color: #FFFFFF;}QSlider::groove:horizontal {border: 1px solid #3A3939;height: 8px;background: #201F1F;margin: 2px 0;border-radius: 2px;}QSlider::handle:horizontal {background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0.0 silver, stop: 0.2 #a8a8a8, stop: 1 #727272);border: 1px solid #3A3939;width: 14px;height: 14px;margin: -4px 0;border-radius: 2px;}QSlider::groove:vertical {border: 1px solid #3A3939;width: 8px;background: #201F1F;margin: 0 0px;border-radius: 2px;}
    QSlider::handle:vertical {background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 silver,  stop: 0.2 #a8a8a8, stop: 1 #727272);border: 1px solid #3A3939;width: 14px;height: 14px;margin: 0 -4px;border-radius: 2px;}QToolButton {background-color: transparent;border: 1px transparent #4A4949;border-radius: 2px;margin: 3px;padding: 3px;}
    QToolButton[popupMode="1"] { /* only for MenuButtonPopup */padding-right: 20px; /* make way for the popup button */border: 1px transparent #4A4949;border-radius: 5px;}
    QToolButton[popupMode="2"] { /* only for InstantPopup */padding-right: 10px; /* make way for the popup button */border: 1px transparent #4A4949;}
    QToolButton:hover, QToolButton::menu-button:hover {background-color: transparent;border: 1px solid #78879b;}
    QToolButton:checked, QToolButton:pressed, QToolButton::menu-button:pressed {background-color: #4A4949;border: 1px solid #78879b;}
    /* the subcontrol below is used only in the InstantPopup or DelayedPopup mode */
    QToolButton::menu-indicator {/*    image: url(:/down_arrow.png);*/top: -7px; left: -2px; /* shift it a bit */}
    QToolButton::menu-button {border: 1px transparent #4A4949;border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;width: 16px;outline: none;}
    QToolButton::menu-arrow {/*    image: url(:/down_arrow.png);*/}
    QToolButton::menu-arrow:open {top: 1px; left: 1px; /* shift it a bit */border: 1px solid #3A3939;}
    QToolBox  {padding: 3px;border: 1px transparent black;}
    QToolBox::tab {color: #b1b1b1;background-color: #302F2F;border: 1px solid #4A4949;
        border-bottom: 1px transparent #302F2F;border-top-left-radius: 5px;border-top-right-radius: 5px;}
    QToolBox::tab:selected { /* italicize selected tabs */font: italic;background-color: #302F2F;border-color: #3d8ec9;}
    QStatusBar::item {border: 1px solid #3A3939;border-radius: 2px;}
    QFrame[height="3"], QFrame[width="3"] {background-color: #444;}
    QSplitter::handle {border: 1px dashed #3A3939;}
    QSplitter::handle:hover {background-color: #787876; border: 1px solid #3A3939;}
    QSplitter::handle:horizontal {width: 1px;}
    QSplitter::handle:vertical {height: 1px;}
    QHeaderView::section {color:#fff;}
    QGroupBox {
        background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #01141c, stop: 1 #FFFFFF);
        border: 2px solid #FFF;
        border-radius: 5px;
        font: bold 30px;
        color : #FFF;
        margin-top: 8ex; /* leave space at the top for the title */
    }
    QGroupBox::title {
        color : #FFF;
        border-top: 2px solid #FFF;
        subcontrol-position: top center; padding: 0 3px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #01141c, stop: 1 #FFFFFF);
        subcontrol-origin: margin;
        subcontrol-position: top center;
        border-top-right-radius: 15px; border-top-left-radius: 15px;
        padding: 15px 50px; background-color: #01141c;color: #FFF;
    }
    QGroupBox > QLabel {
        color : #FFF;
        font : bold 32px;
    }
    QLineEdit { background-color: #787876; color: #FFF; border-color : 2px solid #FFF}

    palette, QMainWindow, QDialog {border: none; background: qlineargradient(x1: 1, y1: 0, x2: 0, y2: 1,
        stop: 0 rgb(25, 96, 104),stop: 0.05 rgb(08, 06, 2),
        stop: 0.5 rgb(95, 100, 104),stop: 0.95 rgb(20, 2, 5),
        stop: 1 rgb(75, 95, 55)); min-height: 50px;}
    QToolBar {
        border: none; background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0.5 rgb(95, 100, 104),stop: 0.95 rgb(20, 2, 5),
        stop: 1 rgb(1, 1, 1)); min-height: 50px;
    }
"""
default = """
    QGroupBox {
        background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #afb2b3, stop: 1 #FFFFFF);
        border: 2px solid #EFFFFF;
        border-radius: 5px;
        font: bold 30px;
        margin-top: 8ex; /* leave space at the top for the title */
    }
    QGroupBox > QLabel {
        color : #000;
        font : bold 32px;
    }
    QGroupBox::title {
        border-top: 2px solid #EFFFFF;
        subcontrol-position: top center; padding: 0 3px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #afb2b3, stop: 1 #FFFFFF);
        subcontrol-origin: margin;
        subcontrol-position: top center;
        border-top-right-radius: 15px; border-top-left-radius: 15px;
        padding: 15px 50px; background-color: #afb2b3;color: rgb(255, 255, 255);
    }
"""
bleu_mari_css = """
    palette, QMainWindow, QDialog {border: none; background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgb(0, 750, 165, 255),stop: 0.05 rgb(31, 164, 227, 255),
        stop: 0.5 #000333,stop: 0.95 rgb(0, 102, 185, 255),
        stop: 1 rgb(0, 75, 165, 255)); min-height: 50px;}
    QToolBar {
        border: none; background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgb(0, 750, 165, 255),stop: 0.05 rgb(31, 164, 227, 255),
        stop: 0.5 #000333,stop: 0.95 rgb(0, 102, 185, 255),
        stop: 1 rgb(0, 75, 165, 255)); min-height: 50px;
    }
    pv--view--View, pv--view--Viewport{
        margin: 0px; border: none; background-color: rgb(255, 255, 255); padding: 0px;
    }
    QToolButton {
        border: none; border-style: flat; color: white; font: bold 10ft;
        min-height: 50px;min-width: 50px;
    }
    QPushButton:hover, QPushButton:pressed,
    QToolButton:hover, QToolButton:pressed {
        background-color: rgb(238, 178, 17, 200);
    }
    QPushButton:checked,
    QToolButton:checked {
        background-color: rgb(255, 255, 255, 50);
    }
    QPushButton {
        padding: 3px;
        border: none;
        border-style: flat;
        border-radius: 4px;
        color: white;
        background-color: rgb(255, 255, 255, 50);
        font: bold 10ft;
        min-height: 20px;
        min-width: 20px;
    }
    /* >>> QToolBar: QLineEdit/QComboBox */
    QLineEdit,
    QComboBox:!editable,
    QSpinBox {
        border: none;
        border-radius: 4px;
        background-color: white;
        padding: 3px;
        min-height: 20px;
    }
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {
        background-color: rgb(200, 200, 200, 255);
    }
    QComboBox:!editable {padding-right: 5px;}
    /* QComboBox gets the "on" state when the popup is open */
    QComboBox:!editable:on, QToolBar > QComboBox::drop-down:editable:on {
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #D3D3D3, stop: 0.4 #D8D8D8,
                                 stop: 0.5 #DDDDDD, stop: 1.0 #E1E1E1);
    }
    QComboBox:on { /* shift the text when the popup opens */
     padding-top: 3px; padding-left: 4px;
    }
    QComboBox::drop-down {
     subcontrol-origin: padding; subcontrol-position: top right;
     width: 20px; border-left-width: 0px;
     border-top-right-radius: 4px; /* same radius as the QComboBox */
     border-bottom-right-radius: 4px;
    }
    QComboBox::down-arrow {image: url(:/icons/down-arrow.png);}
    QComboBox::down-arrow:disabled {image: none;}
    QComboBox::down-arrow:on { /* shift the arrow when popup is open */
     top: 1px; left: 1px;}
    /* <<< QToolBar: QLineEdit/QComboBox */
    /* >>> QDockWidget */
    QDockWidget {
        margin: 0px; background-color: rgb(17, 133, 209,  255);
        border: 0px; padding: 0px; color: rgb(17, 133, 209,  255);
        font-size: 15px; font-weight: bold;
    }
    QDockWidget::title  {
        margin: 0px; text-align: left center;
        background-color: rgb(255, 255, 255, 255);
        border: 0px; color: white; padding: 8px;
    }
    QDockWidget > QWidget{
        margin: 0px; background-color: rgb(17, 133, 209,  255);
        border: 0px; padding: 0px;
    }
    QScrollArea #measureWidget, QScrollArea #dsoTriggerWidget,
    QScrollArea #triggerWidget, QScrollArea #protocolWidget{
        margin: 0px;
        background-color: rgb(17, 133, 209,  255);
        border: 0px;
        padding: 0px;
    }
    #triggerWidget > QTabWidget::pane{
        margin: 0px;
        background-color: rgb(17, 133, 209,  255);
        border: 1px solid rgb(255, 255, 255);
        padding: 0px;
    }
    #triggerWidget > QTabWidget::pane:disabled{
        border: 1px solid rgb(200, 200, 200, 255);
    }
    QTabWidget::pane{
        margin: 0px;
        background-color: rgb(17, 133, 209,  255);
        border: 0px solid rgb(255, 255, 255);
        padding: 0px;
    }
    QCheckBox, QRadioButton, QLabel {
        border: none;
        min-height: 20px;
    }
    QCheckBox::checked, QRadioButton::checked {color: black;}
    QLabel, QCheckBox::unchecked, QRadioButton::unchecked {color: white;}
    QCheckBox, QLabel {padding: 1px 1px 1px 1px; margin: 0px;}
    QLabel:disabled {color: rgb(200, 200, 200, 255);}
    QSlider::groove:horizontal {border: 1px solid #999999;height: 2px;
        margin: 0px 0; left: 10px; right: 10px; border-radius: 4px;}
    QSlider::handle:horizontal {border-image:url(:/icons/slider-handle.png);
        margin-left: -12px; margin-right: -12px;margin-top: -11px; margin-bottom: -11px;}
    QSlider::sub-page:horizontal{background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0,
        stop:0 rgba(17, 133, 209,  255), stop:0.25 rgba(238, 178, 17, 255),
        stop:0.75 rgba(238, 178, 17, 255), stop:1 rgba(17, 133, 209,  255));
        height: 2px; border-radius: 4px;}
    QSlider::add-page:horizontal{
        background: qlineargradient(spread:pad,
        x1:0, y1:1, x2:0, y2:0, stop:0 rgba(17, 133, 209,  255),
        stop:0.25 rgba(255, 255, 255, 255), stop:0.75 rgba(255, 255, 255, 255),
        stop:1 rgba(17, 133, 209,  255)); height: 2px; border-radius: 4px;
    }
    /* <<< QDockWidget */
    QGroupBox {
        background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #011333, stop: 1 #FFFFFF);
        border: 2px solid #FFF; border-radius: 5px; font: bold 30px;
        margin-top: 8ex; /* leave space at the top for the title */
    }
    QGroupBox > QLabel {color : #FFF; font : bold 32px; padding: 1em; margin-Top: 1em}
    QGroupBox::title {
        border-top: 2px solid #FFF; subcontrol-position: top center; padding: 0 3px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #011333, stop: 1 #FFFFFF);
        subcontrol-origin: margin; subcontrol-position: top center;
        border-top-right-radius: 15px; border-top-left-radius: 15px;
        padding: 15px 50px; background-color: #011333; color: rgb(255, 255, 255);
    }
"""


def get_style():
    dic_t = {
        Settings.DF: default,
        Settings.BL: blue_css,
        Settings.DK: drak_ccs,
        Settings.FAD: bleu_mari_css,
    }
    # dic_t = Settings.THEME
    try:
        stt = Settings.get_or_create(id=1)
    except Exception as exc:
        return 1
    # return dic_t.get(stt.theme)
    return dic_t.get(Settings.get(id=1).theme)


theme = get_style()
