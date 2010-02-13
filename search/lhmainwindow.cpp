#include "lhmainwindow.h"
#include "lhsettings.h"
#include "searchpanel.h"
#include "resultview.h"

#include <QSplitter>
#include <QAction>
#include <QMenu>
#include <QMenuBar>
#include <QMessageBox>
#include <QList>

LhMainWindow::LhMainWindow(QWidget *parent) : QMainWindow(parent)
{
	// create main windows
	createUI();

	settings1 = new LhSettings();
}

void LhMainWindow::createUI()
{
	// menus, toolbars, actions, etc
	QAction *quitAct = new QAction(tr("&Quit"), this);
	quitAct->setStatusTip(tr("Quit Linkhive"));
	connect(quitAct, SIGNAL(triggered()), this, SLOT(close()));		//check some stuff before quitting

	QAction *settingsAct = new QAction(tr("&Settings..."), this);
	settingsAct->setStatusTip(tr("Edit settings"));
	connect(settingsAct, SIGNAL(triggered()), this, SLOT(showSettings()));		// how to directly show settings?

	QAction *aboutAct = new QAction(tr("&About"), this);
	aboutAct->setStatusTip(tr("About Linkhive"));
	connect(aboutAct, SIGNAL(triggered()), this, SLOT(about()));

	QMenu *fileMenu = menuBar()->addMenu(tr("&File"));
	fileMenu->addAction(quitAct);
	QMenu *toolsMenu = menuBar()->addMenu(tr("&Tools"));
	toolsMenu->addAction(settingsAct);
	QMenu *helpMenu = menuBar()->addMenu(tr("&Help"));
	helpMenu->addAction(aboutAct);

	// central widget
	QSplitter *splitter = new QSplitter;

	search1 = new SearchPanel(splitter);
	results1 = new ResultView(splitter);

	QList<int> sizeList;					// set sizes in pixels
	sizeList << 300 << 600;
	splitter->setSizes(sizeList);

	// how to declare signal and slot params
	connect(search1, SIGNAL(sendQuery(QStringList)), results1, SLOT(updateCurrentTabQuery(QStringList)));
		// update the filters for the current tab

	setCentralWidget(splitter);
}

// slots
void LhMainWindow::about()
{
	QMessageBox::information(this, tr("About Linkhive"), tr("Linkhive v0.1 by Andree Chea released under the GPL license"));
}

void LhMainWindow::showSettings()
{
	settings1->exec();		// don't care about the return status?
	return;
}
