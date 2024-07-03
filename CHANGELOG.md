# Semantic Versioning Changelog

# [1.1.0](https://github.com/pycasbin/postgresql-watcher/compare/v1.0.0...v1.1.0) (2024-07-03)


### Features

* replace print calls with logging module ([#25](https://github.com/pycasbin/postgresql-watcher/issues/25)) ([1196caf](https://github.com/pycasbin/postgresql-watcher/commit/1196caff8432d0c1ae8f8c1d306c0abcc66894f8))

# [1.0.0](https://github.com/pycasbin/postgresql-watcher/compare/v0.3.0...v1.0.0) (2024-03-29)


### Features

* improve docs ([db23465](https://github.com/pycasbin/postgresql-watcher/commit/db23465064fdcce16a01fa6936e5417a4fc721e1))


### BREAKING CHANGES

* trigger major release

# [0.3.0](https://github.com/pycasbin/postgresql-watcher/compare/v0.2.0...v0.3.0) (2024-03-29)


### Features

* upgrade CI Node.js version to 20 ([8c31f0d](https://github.com/pycasbin/postgresql-watcher/commit/8c31f0df9f95cbc00c955c83c56f12934af30ff8))

# [0.2.0](https://github.com/pycasbin/postgresql-watcher/compare/v0.1.2...v0.2.0) (2023-04-14)


### Bug Fixes

* fix CI's python version and requirements.txt ([dde80ac](https://github.com/pycasbin/postgresql-watcher/commit/dde80ac36fe5d9f5d71b342a33a692c6ad149b87))


### Features

* add SSL options ([#22](https://github.com/pycasbin/postgresql-watcher/issues/22)) ([a1a8f4c](https://github.com/pycasbin/postgresql-watcher/commit/a1a8f4c3d6fa4eb6d874556ffcac5fb26271f86e))

## [0.1.2](https://github.com/pycasbin/postgresql-watcher/compare/v0.1.1...v0.1.2) (2022-05-17)


### Bug Fixes

* made should_reload into a blocking call ([#21](https://github.com/pycasbin/postgresql-watcher/issues/21)) ([6fd89b5](https://github.com/pycasbin/postgresql-watcher/commit/6fd89b5001ccc4e6782294489c40464cfebbf32c))

## [0.1.1](https://github.com/pycasbin/postgresql-watcher/compare/v0.1.0...v0.1.1) (2022-02-07)


### Bug Fixes

* update readme with new parameter and correct callback setter ([7c19709](https://github.com/pycasbin/postgresql-watcher/commit/7c19709967aef5f9efc32b84f46f02b017533e32))

# [0.1.0](https://github.com/pycasbin/postgresql-watcher/compare/v0.0.3...v0.1.0) (2022-02-05)


### Features

* add database name parameter to watcher. ([dd6bed9](https://github.com/pycasbin/postgresql-watcher/commit/dd6bed9fa1326e82980832bdf05a58340c0c06d4))

## [0.0.3](https://github.com/pycasbin/postgresql-watcher/compare/v0.0.2...v0.0.3) (2022-02-05)


### Bug Fixes

* correct requirements and python version support. dev requirement can be installed with: pip install ".[dev]" ([5bd65e8](https://github.com/pycasbin/postgresql-watcher/commit/5bd65e8a4ec85e46691a34ba10d0434659f3a08f))
* Specify a fixed version for nodejs in the release ci workflow ([2e3c5e7](https://github.com/pycasbin/postgresql-watcher/commit/2e3c5e727442db0e1b41a689139bcdc225468dd5))
* upgrade setuptools and wheel before installing deps. Upgrade psycopg2 to latest version (2.9.3) if possible. ([8beff2a](https://github.com/pycasbin/postgresql-watcher/commit/8beff2aef45e164aa27c09298c92886a41afaaf3))

## [0.0.2](https://github.com/pycasbin/postgresql-watcher/compare/v0.0.1...v0.0.2) (2021-07-18)


### Bug Fixes

* CI release failed ([3dd60ea](https://github.com/pycasbin/postgresql-watcher/commit/3dd60ea6b34abab47ef67bae997a646fe4e5d7bd))
* fix `parent_conn` not initialize ([#11](https://github.com/pycasbin/postgresql-watcher/issues/11)) ([48001e0](https://github.com/pycasbin/postgresql-watcher/commit/48001e059d040a04f8f286ad2c6e2f383ea41895))
* Fix for more recent casbin versions and connection send fix ([#12](https://github.com/pycasbin/postgresql-watcher/issues/12)) ([8cc529c](https://github.com/pycasbin/postgresql-watcher/commit/8cc529c0036e6efc27c4d261b354e489a69ad6a4))
