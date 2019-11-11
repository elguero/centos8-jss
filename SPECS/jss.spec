################################################################################
Name:           jss
################################################################################

Summary:        Java Security Services (JSS)
URL:            http://www.dogtagpki.org/wiki/JSS
License:        MPLv1.1 or GPLv2+ or LGPLv2+

Version:        4.6.0
Release:        5%{?_timestamp}%{?_commit_id}%{?dist}
# global         _phase -a1

# To generate the source tarball:
# $ git clone https://github.com/dogtagpki/jss.git
# $ cd jss
# $ git tag v4.5.<z>
# $ git push origin v4.5.<z>
# Then go to https://github.com/dogtagpki/jss/releases and download the source
# tarball.
Source:         https://github.com/dogtagpki/%{name}/archive/v%{version}%{?_phase}/%{name}-%{version}%{?_phase}.tar.gz

# To create a patch for all changes since a version tag:
# $ git format-patch \
#     --stdout \
#     <version tag> \
#     > jss-VERSION-RELEASE.patch
# Patch: jss-VERSION-RELEASE.patch
Patch1:         0001-Disable-buffer-based-tests.patch
Patch2:         0002-Support-LD_FLAGS-from-environment.patch
Patch3:         0003-Remove-legacy-DSA-implementation.patch
Patch4:         0004-JSS-CVE-2019-14823-fix.patch
Patch5:         0005-Add-helper-to-run-a-single-test-case.patch
Patch6:         0006-Add-script-to-add-common-root-CAs.patch
Patch7:         0007-Add-optional-test-case-against-badssl.com.patch

################################################################################
# Build Dependencies
################################################################################

# autosetup
BuildRequires:  git
BuildRequires:  make
BuildRequires:  cmake

BuildRequires:  gcc-c++
BuildRequires:  nspr-devel >= 4.13.1
BuildRequires:  nss-devel >= 3.30
BuildRequires:  nss-tools >= 3.30
BuildRequires:  java-devel
BuildRequires:  jpackage-utils
BuildRequires:  slf4j
BuildRequires:  glassfish-jaxb-api
%if 0%{?rhel} && 0%{?rhel} <= 7
# no slf4j-jdk14
%else
BuildRequires:  slf4j-jdk14
%endif
BuildRequires:  apache-commons-lang
BuildRequires:  apache-commons-codec

BuildRequires:  junit

Requires:       nss >= 3.30
Requires:       java-headless
Requires:       jpackage-utils
Requires:       slf4j
Requires:       glassfish-jaxb-api
%if 0%{?rhel} && 0%{?rhel} <= 7
# no slf4j-jdk14
%else
Requires:       slf4j-jdk14
%endif
Requires:       apache-commons-lang
Requires:       apache-commons-codec

Conflicts:      ldapjdk < 4.20
Conflicts:      idm-console-framework < 1.2
Conflicts:      tomcatjss < 7.3.4
Conflicts:      pki-base < 10.6.5

%description
Java Security Services (JSS) is a java native interface which provides a bridge
for java-based applications to use native Network Security Services (NSS).
This only works with gcj. Other JREs require that JCE providers be signed.

################################################################################
%package javadoc
################################################################################

Summary:        Java Security Services (JSS) Javadocs
Group:          Documentation
Requires:       jss = %{version}-%{release}

%description javadoc
This package contains the API documentation for JSS.

################################################################################
%prep

%autosetup -n %{name}-%{version}%{?_phase} -p 1 -S git

################################################################################
%build

%set_build_flags

[ -z "$JAVA_HOME" ] && export JAVA_HOME=%{_jvmdir}/java

# Enable compiler optimizations
export BUILD_OPT=1

# Generate symbolic info for debuggers
CFLAGS="-g $RPM_OPT_FLAGS"
export CFLAGS

# The Makefile is not thread-safe
rm -rf build && mkdir -p build && cd build
%cmake \
    -DJAVA_HOME=%{java_home} \
    -DJAVA_LIB_INSTALL_DIR=%{_jnidir} \
    ..

%{__make} all
%{__make} javadoc || true
ctest --output-on-failure

################################################################################
%install

# There is no install target so we'll do it by hand

# jars
install -d -m 0755 $RPM_BUILD_ROOT%{_jnidir}
install -m 644 build/jss4.jar ${RPM_BUILD_ROOT}%{_jnidir}/jss4.jar

# We have to use the name libjss4.so because this is dynamically
# loaded by the jar file.
install -d -m 0755 $RPM_BUILD_ROOT%{_libdir}/jss
install -m 0755 build/libjss4.so ${RPM_BUILD_ROOT}%{_libdir}/jss/
pushd  ${RPM_BUILD_ROOT}%{_libdir}/jss
    ln -fs %{_jnidir}/jss4.jar jss4.jar
popd

# javadoc
install -d -m 0755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -rp build/docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -p jss.html $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -p *.txt $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

# No ldconfig is required since this library is loaded by Java itself.
################################################################################
%files

%defattr(-,root,root,-)
%doc jss.html MPL-1.1.txt gpl.txt lgpl.txt
%{_libdir}/*
%{_jnidir}/*

################################################################################
%files javadoc

%defattr(-,root,root,-)
%{_javadocdir}/%{name}-%{version}/

################################################################################
%changelog
* Wed Sep 11 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-5
- Bugzilla #1747987 - CVE 2019-14823 jss: OCSP policy "Leaf and Chain" implicitly trusts the root certificate

* Wed Aug 14 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-4
- Red Hat Bugzilla #1698059 - pki-core implements crypto

* Tue Jul 16 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-3
- Red Hat Bugilla #1721135 - JSS - LD_FLAGS support

* Wed Jun 12 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-2
- Minor updates to release

* Wed Jun 12 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-1
- Rebased to JSS 4.6.0

* Thu Apr 25 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.3-1
- Rebased to JSS 4.5.3

* Fri Aug 10 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-1
- Rebased to JSS 4.5.0

* Tue Aug 07 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.6
- Rebased to JSS 4.5.0-b1

* Tue Aug 07 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.5
- Red Hat Bugzilla #1612063 - Do not override system crypto policy (support TLS 1.3)

* Fri Jul 20 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.4
- Rebased to JSS 4.5.0-a4
- Red Hat Bugzilla #1604462 - jss: FTBFS in Fedora rawhide

* Thu Jul 05 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.3
- Rebased to JSS 4.5.0-a3

* Fri Jun 22 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.2
- Rebased to JSS 4.5.0-a2

* Fri Jun 15 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.1
- Rebased to JSS 4.5.0-a1
