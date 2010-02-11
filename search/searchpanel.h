#ifndef SEARCHPANEL_H
#define SEARCHPANEL_H
#include <QWidget>

class QPlainTextEdit;
class QLineEdit;

class SearchPanel : public QWidget
{
	Q_OBJECT

	public:
		SearchPanel(QWidget *parent = 0);

	signals:
		void sendQuery(QStringList);

	private slots:
		// search pressed, so parse and emit sendQuery signal containing new search stuff
		void searchClicked();

	private:
		QLineEdit *fieldText;
		QLineEdit *tableText;
		QPlainTextEdit *queryText;

};
#endif
