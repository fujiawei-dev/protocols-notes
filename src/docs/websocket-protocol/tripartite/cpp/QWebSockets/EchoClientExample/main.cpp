// Generated by [Toolkit-Py](https://github.com/fujiawei-dev/toolkit-py) Generator
// Created at 2022-03-12 14:47:44.715750, Version 0.10.7
#include <QtCore/QCoreApplication>
#include "echoclient.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    EchoClient client(QUrl(QStringLiteral("ws://localhost:8089")));
    QObject::connect(&client, &EchoClient::closed, &a, &QCoreApplication::quit);

    return QCoreApplication::exec();
}
