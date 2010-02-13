#ifndef LHSETTINGS_H
#define LHSETTINGS_H

#include <QDialog>
#include <QWidget>

class QTabWidget;

class LhSettings : public QDialog
{
	Q_OBJECT

	public:
		LhSettings(QWidget *parent = 0);

	private slots:
		void saveAccept();
	private:
		QTabWidget *tabWidget;			// different tabs added here
};

class TableTab : public QWidget
{
	Q_OBJECT

	public:
		TableTab(QWidget *parent = 0);
		
	private:
};
#endif
