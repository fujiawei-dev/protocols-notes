// Generated by Toolkit-Py[v0.16.8] Generator. Created at 2022-04-07 08:44:23.559895.

#ifndef DIGEST_AUTH_QT5__SERIAL_PORT_H
#define DIGEST_AUTH_QT5__SERIAL_PORT_H

#include <QObject>
#include <QSerialPort>
#include <QSettings>

class SerialPort : public QObject {
    Q_OBJECT

public:
    explicit SerialPort(QObject *parent = nullptr);

    static void PrintSerialPorts();

    bool DebugMode() const;
    void InitConfig(bool, QSettings *);

    void Open();
    void Close();

    QByteArray WriteSync(const QByteArray &byteArray);
    QByteArray WriteSyncFromHex(const QByteArray &hexString);


public slots:
    void onExit();

private:
    bool debugMode = true;

    void beforeInitConfig();
    void afterInitConfig();

    // variables from config file
    QSettings *conf{};

    QString portName;
    QSerialPort *serialPort;
};

#endif//DIGEST_AUTH_QT5__SERIAL_PORT_H
