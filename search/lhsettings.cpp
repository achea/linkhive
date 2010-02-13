#include "lhsettings.h"

#include <QTabWidget>
#include <QVBoxLayout>
#include <QLabel>
#include <QDialogButtonBox>
#include <QMessageBox>

LhSettings::LhSettings(QWidget *parent) : QDialog(parent)
{
	tabWidget = new QTabWidget;
	tabWidget->addTab(new TableTab(), tr("Tables"));

	QDialogButtonBox *buttonBox = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);

	connect(buttonBox, SIGNAL(accepted()), this, SLOT(saveAccept()));		// what about in between?
	connect(buttonBox, SIGNAL(rejected()), this, SLOT(reject()));

	QVBoxLayout* mainLayout = new QVBoxLayout;
	mainLayout->addWidget(tabWidget);
	mainLayout->addWidget(buttonBox);

	setLayout(mainLayout);
}

void LhSettings::saveAccept()
{
	// save all settings
	QMessageBox::information(this,"You're done!","Configured! :)");
	this->accept();
}

/* TableTab */
// lets user enter database connection settings for each table (that stores data for social news site stories, or personal annotation notes, or --)
TableTab::TableTab(QWidget *parent) : QWidget(parent)
{
	QLabel *label1 = new QLabel(tr("Hi!"));
	QVBoxLayout *layout1 = new QVBoxLayout;
	layout1->addWidget(label1);
	setLayout(layout1);
}
