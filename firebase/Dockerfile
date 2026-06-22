# ローカル開発用 Firebase Auth Emulator
FROM node:20-alpine

# Auth Emulator 本体は firebase-tools に同梱されている (Java 不要)
RUN npm install -g firebase-tools

WORKDIR /firebase
COPY firebase.json .firebaserc ./

EXPOSE 9099 4000

CMD ["firebase", "emulators:start", "--only", "auth", "--project", "fairyhobby"]
