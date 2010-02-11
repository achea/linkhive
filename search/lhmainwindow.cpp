#include "lhmainwindow.h"
#include "searchpanel.h"
#include "resultview.h"

#include <QSplitter>

LhMainWindow::LhMainWindow(QWidget *parent) : QMainWindow(parent)
{
	QSplitter *splitter = new QSplitter;

	search1 = new SearchPanel(splitter);		// pointer to data
	results1 = new ResultView(splitter);		// pointer to data
											// the data is stored here in LhMainWindow though

	// how to declare signal and slot params
	connect(search1, SIGNAL(sendQuery(QStringList)), results1, SLOT(updateCurrentTabQuery(QStringList)));
		// update the filters for the current tab

	setCentralWidget(splitter);
}
