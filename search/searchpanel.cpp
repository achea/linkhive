#include "searchpanel.h"
#include <QPlainTextEdit>
#include <QLineEdit>
#include <QLabel>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QVBoxLayout>
#include <QPushButton>
#include <QMessageBox>
#include <QStringList>

SearchPanel::SearchPanel(QWidget *parent) : QWidget(parent)
{
	// select and fields
	fieldText = new QLineEdit;
	QLabel *findLabel = new QLabel(tr("S&ELECT "));
	findLabel->setBuddy(fieldText);

	// table
	tableText = new QLineEdit;
	QLabel *tableLabel = new QLabel(tr("&FROM "));
	tableLabel->setBuddy(tableText);
	
	// where
	queryText = new QPlainTextEdit;
	QLabel *queryLabel = new QLabel(tr("&WHERE "));
	queryLabel->setBuddy(queryText);

	// search button
	QPushButton *searchButton = new QPushButton(tr("&Search"));
	// emit a signal
	QObject::connect(searchButton, SIGNAL(clicked()), this, SLOT(searchClicked()));

	// grid layout as a form
	QGridLayout *gLayout = new QGridLayout;
	gLayout->addWidget(findLabel,0,0);
	gLayout->addWidget(fieldText,0,1);
	gLayout->addWidget(tableLabel,1,0);
	gLayout->addWidget(tableText,1,1);
	gLayout->addWidget(queryLabel,2,0);
	gLayout->addWidget(queryText,2,1);

	// search layout
	QHBoxLayout *searchLayout = new QHBoxLayout;
	searchLayout->addStretch();
	searchLayout->addWidget(searchButton);

	// main layout
	QVBoxLayout *mainLayout = new QVBoxLayout;
	mainLayout->addLayout(gLayout);
	mainLayout->addLayout(searchLayout);
	mainLayout->addStretch();

	this->setLayout(mainLayout);
}

void SearchPanel::updateCurrentQuery(const QStringList& queryList)
{
	// connected to currentQueryChanged signal from ResultsView
	// updates the lineedits from queryList

	fieldText->setText(queryList.at(0));
	tableText->setText(queryList.at(1));
	// QPlainTextEdit
	queryText->clear();
	queryText->insertPlainText(queryList.at(2));
}

// slot
void SearchPanel::searchClicked()
{
	QStringList queryList;		// not dynamic
	bool valid = true;

	// send the fieldText, tableText, and queryText
	queryList << fieldText->text() << tableText->text() << queryText->toPlainText();

	QStringList::const_iterator i;
	for (i = queryList.constBegin(); i != queryList.constEnd(); i++)
	{
		// i is a pointer?
		if (i->isEmpty())
			valid = false;
	}

	if (!valid)
	{
		QMessageBox::information(this,"Missing fields",tr("One or more fields are empty"));
		return;
	}

	// otherwise, it is good
	emit sendQuery(queryList);
}
