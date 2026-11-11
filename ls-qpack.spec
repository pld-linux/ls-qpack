#
# Conditional build:
%bcond_without	static_libs	# static library
%bcond_without	tests		# unit tests

Summary:	QPACK compression library for use with HTTP/3
Summary(pl.UTF-8):	Biblioteka kompresji QPACK do użycia z HTTP/3
Name:		ls-qpack
Version:	2.7.0
Release:	1
License:	MIT
Group:		Libraries
#Source0Download: https://github.com/litespeedtech/ls-qpack/releases
Source0:	https://github.com/litespeedtech/ls-qpack/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	4986f8c84ca7d61a3d4aee85132e8996
Patch0:		ls-qpack-fuzz-decode-fortify.patch
Patch1:		ls-qpack-libm.patch
URL:		https://github.com/litespeedtech/ls-qpack
BuildRequires:	cmake >= 3.1
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.605
BuildRequires:	xxHash-devel
%if %{with tests}
BuildRequires:	bash
BuildRequires:	perl-base
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
ls-qpack is a full-featured, tested, and fast QPACK library. QPACK is
the compression mechanism used by HTTP/3 to compress HTTP headers.

%description -l pl.UTF-8
ls-qpack to w pełni funkcjonalna, przetestowana i szybka biblioteka
QPACK. QPACK to mechanizm kompresji używany przez HTTP/3 do
kompresowania nagłówków HTTP.

%package devel
Summary:	Header files for ls-qpack library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki ls-qpack
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for ls-qpack library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki ls-qpack.

%package static
Summary:	Static ls-qpack library
Summary(pl.UTF-8):	Statyczna biblioteka ls-qpack
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static ls-qpack library.

%description static -l pl.UTF-8
Statyczna biblioteka ls-qpack.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1

%build
# note: .pc file creation expects include and lib dirs relative to CMAKE_INSTALL_PREFIX
%if %{with static_libs}
%cmake -B build-static \
	-DCMAKE_INSTALL_INCLUDEDIR=include \
	-DCMAKE_INSTALL_LIBDIR=%{_lib} \
	-DBUILD_SHARED_LIBS=OFF \
	-DLSQPACK_BIN=OFF \
	-DLSQPACK_XXH=OFF

%{__make} -C build-static
%endif

%cmake -B build \
	-DCMAKE_INSTALL_INCLUDEDIR=include \
	-DCMAKE_INSTALL_LIBDIR=%{_lib} \
	-DBUILD_SHARED_LIBS=ON \
	-DLSQPACK_BIN=OFF \
	-DLSQPACK_XXH=OFF

%{__make} -C build

%if %{with tests}
# LSQPACK_TESTS builds the library itself in devel mode, so test a separate build
%cmake -B build-test \
	-DBUILD_SHARED_LIBS=OFF \
	-DLSQPACK_TESTS=ON \
	-DLSQPACK_XXH=OFF

%{__make} -C build-test
ctest --test-dir build-test --output-on-failure
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with static_libs}
%{__make} -C build-static install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc CHANGELOG LICENSE README.md
%{_libdir}/libls-qpack.so.*.*.*
%ghost %{_libdir}/libls-qpack.so.2

%files devel
%defattr(644,root,root,755)
%{_libdir}/libls-qpack.so
%{_includedir}/lsqpack.h
%{_includedir}/lsxpack_header.h
%{_libdir}/cmake/ls-qpack
%{_pkgconfigdir}/lsqpack.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libls-qpack.a
%endif
