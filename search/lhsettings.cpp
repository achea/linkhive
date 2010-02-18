#include "lhsettings.h"
#include "lhglobals.h"

#include <QTabWidget>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QVBoxLayout>
#include <QFormLayout>
#include <QLabel>
#include <QDialogButtonBox>
#include <QMessageBox>

#include <QGroupBox>
#include <QComboBox>
#include <QPushButton>
#include <QLineEdit>

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
	// assume that the LhGlobals has already created tables
	// TODO typedefs to match so when need to change, only need to change in one typedef
	// TODO how to update on focus?
	// create a local copy, so that current isn't modified
	QHash<QString,int> tableNames = LhGlobals::Instance().tableNames;
	QHash<int,QHash<QString,QString> > connectionConfigs = LhGlobals::Instance().connectionConfigs;
	
	// tableGroup has the QComboBox and two QPushButtons
	QGroupBox *tableGroup = new QGroupBox(tr("Tables"));
	QComboBox *tableComboBox = new QComboBox;

	QString name;
	foreach( name, tableNames.keys())
	{
		tableComboBox->addItem(name);
	}

	// TODO icons for pushbuttons
	QPushButton *tableAddButton = new QPushButton(tr("Add"));
	QPushButton *tableDelButton = new QPushButton(tr("Delete"));
	QLabel *tableLabel1 = new QLabel(tr("Table:"));

	QHBoxLayout *tableLayout = new QHBoxLayout;
	tableLayout->addWidget(tableLabel1);
	tableLayout->addWidget(tableComboBox);
	tableLayout->addWidget(tableAddButton);
	tableLayout->addWidget(tableDelButton);
	tableGroup->setLayout(tableLayout);

	// now the config group
	QGroupBox *configGroup = new QGroupBox(tr("Database configuration"));
	// two layouts in VBox, top is HBox and bottom is Grid
	QComboBox *configComboBox = new QComboBox;

	QPushButton *configAddButton = new QPushButton(tr("Add"));
	QPushButton *configDelButton = new QPushButton(tr("Delete"));
	QLabel *configLabel1 = new QLabel(tr("Config:"));

	QHBoxLayout *layout1 = new QHBoxLayout;
	layout1->addWidget(configLabel1);
	layout1->addWidget(configComboBox);
	layout1->addWidget(configAddButton);
	layout1->addWidget(configDelButton);

	// now the db form
	QComboBox *configDbType = new QComboBox;
	QLineEdit *configDbHost = new QLineEdit;
	QLineEdit *configDbUser = new QLineEdit;
	QLineEdit *configDbPass = new QLineEdit;
	QLineEdit *configDbDb = new QLineEdit;

	QFormLayout *configDbLayout = new QFormLayout;
	configDbLayout->addRow(tr("Type:"),configDbType);
	configDbLayout->addRow(tr("Host:"),configDbHost);
	configDbLayout->addRow(tr("User:"),configDbUser);
	configDbLayout->addRow(tr("Pass:"),configDbPass);
	configDbLayout->addRow(tr("Db:"),configDbDb);

	// the config group
	QVBoxLayout *configLayout = new QVBoxLayout;
	configLayout->addLayout(layout1);
	configLayout->addLayout(configDbLayout);
	configGroup->setLayout(configLayout);
	
	// the tab widget has both groups
	QVBoxLayout *mainLayout = new QVBoxLayout;
	mainLayout->addWidget(tableGroup);
	mainLayout->addWidget(configGroup);
	mainLayout->addStretch();
	setLayout(mainLayout);
}
