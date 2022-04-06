/*
 * @Date: 2022.04.06 20:05
 * @Description: Omit
 * @LastEditors: Rustle Karl
 * @LastEditTime: 2022.04.06 20:05
 */
#ifndef DIGEST_AUTH_QT5__HTTP_AUTH_H
#define DIGEST_AUTH_QT5__HTTP_AUTH_H

#include <QByteArray>

typedef struct {
    QByteArray Username;
    QByteArray Password;
    QByteArray Method;
    QByteArray Uri;
    QByteArray Realm;
    QByteArray Nonce;
    QByteArray Cnonce;
    QByteArray Nc;
    QByteArray Qop;
    QByteArray Algorithm;
    QByteArray Response;
} Digest;

QByteArray getRandomHex(const int &length);

QString generateDigestAuthentication(Digest &digest);

#endif//DIGEST_AUTH_QT5__HTTP_AUTH_H
