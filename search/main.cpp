#include <QApplication>

#include "connection.h"
#include "lhmainwindow.h"

int main(int argc, char **argv)
{
	QApplication app(argc, argv);

	if (!createConnection())
		return 1;

	LhMainWindow window1;
	window1.show();

	return app.exec();
}
