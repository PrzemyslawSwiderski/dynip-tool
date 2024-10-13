# Amazon JDK image https://hub.docker.com/_/amazoncorretto
FROM amazoncorretto:21.0.4

COPY . .

RUN ./gradlew pipInstall

ENTRYPOINT ["./gradlew", "runIpUpdate"]
