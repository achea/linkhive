#ifndef LHMAINWINDOW_H
#define LHMAINWINDOW_H

#include <QMainWindow>

class SearchPanel;
class ResultView;
class LhSettings;
class QKeyEvent;

class LhMainWindow : public QMainWindow
{
	Q_OBJECT

	public:
		LhMainWindow(QWidget *parent=0);

	private slots:
		// menu related slots
		//void close();		// already inherited
		void about();
		void showSettings();

	protected:
		void keyPressEvent(QKeyEvent*);
	
	private:
		void createUI();

		SearchPanel *search1;
		ResultView *results1;
		LhSettings *settings1;
};

#endif
