#include <QApplication>
#include <QtDebug>

#include "lhglobals.h"
#include "lhmainwindow.h"

int main(int argc, char **argv)
{
	QApplication app(argc, argv);

	if (!LhGlobals::Instance().readSettings2())
		return 1;
	if (!LhGlobals::Instance().createConnections())
		return 1;

	LhMainWindow window1;
	window1.show();

	bool status1 = app.exec();
	bool status2 = LhGlobals::Instance().closeAllDbs();
	Q_ASSERT(status2);
	return (int)(status1 || status2);
}
