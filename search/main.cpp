#include <QApplication>
#include <QtDebug>

#include "lhglobals.h"
#include "lhmainwindow.h"
#include "datatypes.h"

int main(int argc, char **argv)
{
	QApplication app(argc, argv);
	app.setApplicationName(LINKHIVE_NAME);			// for QSettings
													// oops, readSettings2() is called outside of the application
	app.setApplicationVersion(LINKHIVE_VERSION);

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
