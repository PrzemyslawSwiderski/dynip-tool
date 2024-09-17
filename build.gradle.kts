import com.pswidersk.gradle.python.VenvTask

plugins {
    id("com.pswidersk.python-plugin") version "2.7.3"
}

pythonPlugin {
    pythonVersion = "3.12.4"
    condaInstaller = "Miniconda3"
    condaVersion = "py312_24.5.0-0"

    val homePath = providers.systemProperty("user.home").get()
    installDir = file(homePath).resolve(".gradle/python")
}

tasks {

    register<VenvTask>("condaInfo") {
        venvExec = "conda"
        args = listOf("info")
    }

    register<VenvTask>("pipInstall") {
        venvExec = "pip"
        args = listOf("install", "-r", "requirements.txt")

        doLast {
            layout.projectDirectory.file("configs/config.example.yaml").asFile
                .copyTo(layout.projectDirectory.file("configs/config.yaml").asFile)
        }
    }

    register<VenvTask>("runIpUpdate") {
        args = listOf("src/ip_update.py")
    }

}
