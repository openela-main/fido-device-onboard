%define dracutlibdir %{_prefix}/lib/dracut
%bcond_without check
%global __cargo_skip_build 0
%global __cargo_is_lib() false
%global forgeurl https://github.com/fedora-iot/fido-device-onboard-rs

Version:        0.4.5

%forgemeta

Name:           fido-device-onboard
Release:        1%{?dist}
Summary:        An implementation of the FIDO Device Onboard Specification written in rust

License:        BSD
URL:            %{forgeurl}
Source:         %{forgesource}
%if "%{?commit}" != ""
Source1:        %{name}-rs-%{commit}-vendor-patched.tar.gz
%else
Source1:        %{name}-rs-%{version}-vendor-patched.tar.gz
%endif

Patch0:         kdf-debug-profile.patch

ExclusiveArch:  %{rust_arches}
# RHBZ 1869980
ExcludeArch:    s390x i686 %{power64}

%if 0%{?rhel} && !0%{?eln}
BuildRequires:  rust-toolset
%else
BuildRequires:  rust-packaging
%endif
BuildRequires: systemd-rpm-macros
BuildRequires: openssl-devel
BuildRequires: golang
BuildRequires: tpm2-tss-devel
BuildRequires: cryptsetup-devel
BuildRequires: clang-devel

%description
%{summary}.

%prep
%forgesetup
%if 0%{?rhel} && !0%{?eln}
%cargo_prep -V 1
%else
%cargo_prep
%endif
%patch0 -p1

%build
%{__cargo} build --release --features "openssl-kdf/deny_custom,fdo-data-formats/use_noninteroperable_kdf"

%install
install -D -m 0755 -t %{buildroot}%{_libexecdir}/fdo target/release/fdo-client-linuxapp
install -D -m 0755 -t %{buildroot}%{_libexecdir}/fdo target/release/fdo-manufacturing-client
install -D -m 0755 -t %{buildroot}%{_libexecdir}/fdo target/release/fdo-manufacturing-server
install -D -m 0755 -t %{buildroot}%{_libexecdir}/fdo target/release/fdo-owner-onboarding-server
install -D -m 0755 -t %{buildroot}%{_libexecdir}/fdo target/release/fdo-rendezvous-server
install -D -m 0755 -t %{buildroot}%{_libexecdir}/fdo target/release/fdo-serviceinfo-api-server
# duplicates as needed by AIO command
install -D -m 0755 -t %{buildroot}%{_libexecdir}/fdo target/release/fdo-owner-tool
install -D -m 0755 -t %{buildroot}%{_libexecdir}/fdo target/release/fdo-admin-tool
install -D -m 0755 -t %{buildroot}%{_bindir} target/release/fdo-owner-tool
install -D -m 0755 -t %{buildroot}%{_bindir} target/release/fdo-admin-tool
install -D -m 0644 -t %{buildroot}%{_unitdir} examples/systemd/*
install -D -m 0644 -t %{buildroot}%{_docdir}/fdo examples/config/*
mkdir -p %{buildroot}%{_sysconfdir}/fdo
# 52fdo
install -D -m 0755 -t %{buildroot}%{dracutlibdir}/modules.d/52fdo dracut/52fdo/module-setup.sh
install -D -m 0755 -t %{buildroot}%{dracutlibdir}/modules.d/52fdo dracut/52fdo/manufacturing-client-generator
install -D -m 0755 -t %{buildroot}%{dracutlibdir}/modules.d/52fdo dracut/52fdo/manufacturing-client-service
install -D -m 0755 -t %{buildroot}%{dracutlibdir}/modules.d/52fdo dracut/52fdo/manufacturing-client.service

%package -n fdo-init
Summary: dracut module for device initialization
%description -n fdo-init
%{summary}

%files -n fdo-init
%license LICENSE
%{dracutlibdir}/modules.d/52fdo/*
%{_libexecdir}/fdo/fdo-manufacturing-client

%package -n fdo-owner-onboarding-server
Summary: FDO Owner Onboarding Server implementation
%description -n fdo-owner-onboarding-server
%{summary}

%files -n fdo-owner-onboarding-server
%license LICENSE
%{_libexecdir}/fdo/fdo-owner-onboarding-server
%{_libexecdir}/fdo/fdo-serviceinfo-api-server
%{_docdir}/fdo/serviceinfo-api-server.yml
%{_unitdir}/fdo-serviceinfo-api-server.service
%{_docdir}/fdo/owner-onboarding-server.yml
%{_unitdir}/fdo-owner-onboarding-server.service

%post -n fdo-owner-onboarding-server
%systemd_post fdo-owner-onboarding-server.service
%systemd_post fdo-serviceinfo-api-server.service

%preun -n fdo-owner-onboarding-server
%systemd_preun fdo-owner-onboarding-server.service
%systemd_post fdo-serviceinfo-api-server.service

%postun -n fdo-owner-onboarding-server
%systemd_postun_with_restart fdo-owner-onboarding-server.service
%systemd_postun_with_restart fdo-serviceinfo-api-server.service

%package -n fdo-rendezvous-server
Summary: FDO Rendezvous Server implementation
%description -n fdo-rendezvous-server
%{summary}

%files -n fdo-rendezvous-server
%license LICENSE
%{_libexecdir}/fdo/fdo-rendezvous-server
%{_docdir}/fdo/rendezvous-server.yml
%{_unitdir}/fdo-rendezvous-server.service

%post -n fdo-rendezvous-server
%systemd_post fdo-rendezvous-server.service

%preun -n fdo-rendezvous-server
%systemd_preun fdo-rendezvous-server.service

%postun -n fdo-rendezvous-server
%systemd_postun_with_restart fdo-rendezvous-server.service

%package -n fdo-manufacturing-server
Summary: FDO Manufacturing Server implementation
%description -n fdo-manufacturing-server
%{summary}

%files -n fdo-manufacturing-server
%license LICENSE
%{_libexecdir}/fdo/fdo-manufacturing-server
%{_docdir}/fdo/manufacturing-server.yml
%{_unitdir}/fdo-manufacturing-server.service

%post -n fdo-manufacturing-server
%systemd_post fdo-manufacturing-server.service

%preun -n fdo-manufacturing-server
%systemd_preun fdo-manufacturing-server.service

%postun -n fdo-manufacturing-server
%systemd_postun_with_restart fdo-manufacturing-server.service

%package -n fdo-client
Summary: FDO Client implementation
Requires: clevis
Requires: clevis-luks
Requires: cryptsetup
%description -n fdo-client
%{summary}

%files -n fdo-client
%license LICENSE
%{_libexecdir}/fdo/fdo-client-linuxapp
%{_unitdir}/fdo-client-linuxapp.service

%post -n fdo-client
%systemd_post fdo-client-linuxapp.service

%preun -n fdo-client
%systemd_preun fdo-client-linuxapp.service

%postun -n fdo-client
%systemd_postun_with_restart fdo-client-linuxapp.service

%package -n fdo-owner-cli
Summary: FDO Owner tools implementation
%description -n fdo-owner-cli
%{summary}

%files -n fdo-owner-cli
%license LICENSE
%{_bindir}/fdo-owner-tool
%{_libexecdir}/fdo/fdo-owner-tool

%package -n fdo-admin-cli
Summary: FDO admin tools implementation
Requires: fdo-manufacturing-server
Requires: fdo-init
Requires: fdo-client
Requires: fdo-rendezvous-server
Requires: fdo-owner-onboarding-server
Requires: fdo-owner-cli
%description -n fdo-admin-cli
%{summary}

%files -n fdo-admin-cli
%license LICENSE
%{_bindir}/fdo-admin-tool
%{_libexecdir}/fdo/fdo-admin-tool
%{_unitdir}/fdo-aio.service
%dir %{_sysconfdir}/fdo

%post -n fdo-admin-cli
%systemd_post fdo-aio.service

%preun -n fdo-admin-cli
%systemd_preun fdo-aio.service

%postun -n fdo-admin-cli
%systemd_postun_with_restart fdo-aio.service

%changelog
* Tue Mar 29 2022 Antonio Murdaca <runcom@linux.com> - 0.4.5-1
- bump to 0.4.5

* Fri Feb 25 2022 Antonio Murdaca <runcom@linux.com> - 0.4.0-8
- attempt #1 to fix checksums

* Fri Feb 25 2022 Antonio Murdaca <runcom@linux.com> - 0.4.0-7
- patch the right vendor/tss-esapi-sys

* Fri Feb 25 2022 Antonio Murdaca <runcom@linux.com> - 0.4.0-6
- patch Cargo.toml to ignore Cargo.lock for hash checks of tss-esapi-sys

* Fri Feb 25 2022 Antonio Murdaca <runcom@linux.com> - 0.4.0-5
- patch tss-esapi-sys/build.rs to require 2.3.2

* Thu Feb 24 2022 Antonio Murdaca <runcom@linux.com> - 0.4.0-4
- rebuilt with tpm2-tss-devel build require

* Thu Feb 24 2022 Antonio Murdaca <runcom@linux.com> - 0.4.0-3
- rebuilt to use the correct patch for the 0.4.0 source

* Thu Feb 24 2022 Antonio Murdaca <runcom@linux.com> - 0.4.0-2
- rebuilt to use the correct 0.4.0 source archive

* Thu Feb 24 2022 Antonio Murdaca <runcom@linux.com> - 0.4.0-1
- upgrade to 0.4.0

* Thu Feb 03 2022 Antonio Murdaca <runcom@linux.com> - 0.3.0-4
- revert and add missing %patch call

* Thu Feb 03 2022 Antonio Murdaca <runcom@linux.com> - 0.3.0-3
- rebuilt to drop commit conditional or patch doesn't work

* Thu Feb 03 2022 Antonio Murdaca <runcom@linux.com> - 0.3.0-2
- rebuilt to drop faulty conditional

* Tue Feb 01 2022 Antonio Murdaca <runcom@linux.com> - 0.3.0-1
- bump to v0.3.0

* Mon Jan 10 2022 Antonio Murdaca <runcom@linux.com> - 0.2.0-5
- rebuilt dropping vendored exe(s) files (dll and .a)

* Sat Dec 11 2021 Antonio Murdaca <runcom@linux.com> - 0.2.0-4
- Restore soname, add golang to BuildRequires

* Sat Dec 11 2021 Antonio Murdaca <runcom@linux.com> - 0.2.0-3
- disable libfdo-data soname

* Sat Dec 11 2021 Antonio Murdaca <runcom@linux.com> - 0.2.0-2
- rebuilt

* Fri Dec 10 2021 Antonio Murdaca <runcom@linux.com> - 0.2.0-1
- bump to 0.2.0

* Wed Nov 17 2021 Antonio Murdaca <runcom@linux.com> - 0.1.0-2
- rebuilt

* Tue Oct 5 2021 Antonio Murdaca <amurdaca@redhat.com> - 0.1.0-1
- initial release
