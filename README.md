# DNS IP records update tool

## About

This project was based on [dynamic-dns-name.com](https://github.com/DanHerbert/dynamic-dns-name.com). It modifies it a
little. Main job is to call DNS provider API in order to adjust the IP associated with a specific DNS name.

Changes:

* possibility to build and trigger it with Gradle
* replaced email notification with optional Gist GitHub publishing
* it is now possible to pass multiple `wan_ip_endpoints` so that the other `urls` can be used as backup source.
* separated source files into `src`, `configs` and `services`

In the below sections there are described the steps to set up a service in Linux system to update DNS records
automatically.

## Installing Python and PIP dependencies

Run:

```commandline
./gradlew pipInstall 
```

or on Windows:

```commandline
gradlew pipInstall
```

## Config file adjustment

Please adjust the `configs/config.yaml` with your values before running the scripts.

## Running Python script directly

It is possible to invoke the script directly by running:

```commandline
./gradlew runIpUpdate
```
