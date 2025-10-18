@Override
    public final void func_65815(String name, String value) throws HpackException {
        if (log.isDebugEnabled()) {
            log.debug(sm.getString("stream.header.debug", getConnectionId(), getIdentifier(),
                    name, value));
        }

                if (!name.toLowerCase(Locale.US).equals(name)) {
            throw new HpackException(sm.getString("stream.header.case",
                    getConnectionId(), getIdentifier(), name));
        }

        if ("connection".equals(name)) {
            throw new HpackException(sm.getString("stream.header.connection",
                    getConnectionId(), getIdentifier()));
        }

        if ("te".equals(name)) {
            if (!"trailers".equals(value)) {
                throw new HpackException(sm.getString("stream.header.te",
                        getConnectionId(), getIdentifier(), value));
            }
        }

        if (headerStateErrorMsg != null) {
                                    return;
        }

        boolean pseudoHeader = name.charAt(0) == ':';

        if (pseudoHeader && headerState != HEADER_STATE_PSEUDO) {
            headerStateErrorMsg = sm.getString("stream.header.unexpectedPseudoHeader",
                    getConnectionId(), getIdentifier(), name);
                        return;
        }

        if (headerState == HEADER_STATE_PSEUDO && !pseudoHeader) {
            headerState = HEADER_STATE_REGULAR;
        }

        switch(name) {
        case ":method": {
            if (coyoteRequest.method().isNull()) {
                coyoteRequest.method().setString(value);
            } else {
                throw new HpackException(sm.getString("stream.header.duplicate",
                        getConnectionId(), getIdentifier(), ":method" ));
            }
            break;
        }
        case ":scheme": {
            if (coyoteRequest.scheme().isNull()) {
                coyoteRequest.scheme().setString(value);
            } else {
                throw new HpackException(sm.getString("stream.header.duplicate",
                        getConnectionId(), getIdentifier(), ":scheme" ));
            }
            break;
        }
        case ":path": {
            if (!coyoteRequest.requestURI().isNull()) {
                throw new HpackException(sm.getString("stream.header.duplicate",
                        getConnectionId(), getIdentifier(), ":path" ));
            }
            if (value.length() == 0) {
                throw new HpackException(sm.getString("stream.header.noPath",
                        getConnectionId(), getIdentifier()));
            }
            int queryStart = value.indexOf('?');
            if (queryStart == -1) {
                coyoteRequest.requestURI().setString(value);
                coyoteRequest.decodedURI().setString(
                        coyoteRequest.getURLDecoder().convert(value, false));
            } else {
                String uri = value.substring(0, queryStart);
                String query = value.substring(queryStart + 1);
                coyoteRequest.requestURI().setString(uri);
                coyoteRequest.decodedURI().setString(
                        coyoteRequest.getURLDecoder().convert(uri, false));
                coyoteRequest.queryString().setString(query);
            }
            break;
        }
        case ":authority": {
            if (coyoteRequest.serverName().isNull()) {
                int i = value.lastIndexOf(':');
                if (i > -1) {
                    coyoteRequest.serverName().setString(value.substring(0, i));
                    coyoteRequest.setServerPort(Integer.parseInt(value.substring(i + 1)));
                } else {
                    coyoteRequest.serverName().setString(value);
                }
            } else {
                throw new HpackException(sm.getString("stream.header.duplicate",
                        getConnectionId(), getIdentifier(), ":authority" ));
            }
            break;
        }
        case "cookie": {
                                    if (cookieHeader == null) {
                cookieHeader = new StringBuilder();
            } else {
                cookieHeader.append("; ");
            }
            cookieHeader.append(value);
            break;
        }
        default: {
            if (headerState == HEADER_STATE_TRAILER && !handler.isTrailerHeaderAllowed(name)) {
                break;
            }
            if ("expect".equals(name) && "100-continue".equals(value)) {
                coyoteRequest.setExpectation(true);
            }
            if (pseudoHeader) {
                headerStateErrorMsg = sm.getString("stream.header.unknownPseudoHeader",
                        getConnectionId(), getIdentifier(), name);
            }

            if (headerState == HEADER_STATE_TRAILER) {
                                coyoteRequest.getTrailerFields().put(name, value);
            } else {
                coyoteRequest.getMimeHeaders().addValue(name).setString(value);
            }
        }
        }
    }
private synchronized TaskBuilder func_65815() throws IOException {
        File projectsDir = new File(root,"jobs");
        if(!projectsDir.getCanonicalFile().isDirectory() && !projectsDir.mkdirs()) {
            if(projectsDir.exists())
                throw new IOException(projectsDir+" is not a directory");
            throw new IOException("Unable to create "+projectsDir+"\nPermission issue? Please create this directory manually.");
        }
        File[] subdirs = projectsDir.listFiles();

        final Set<String> loadedNames = Collections.synchronizedSet(new HashSet<String>());

        TaskGraphBuilder g = new TaskGraphBuilder();
        Handle loadJenkins = g.requires(EXTENSIONS_AUGMENTED).attains(JOB_LOADED).add("Loading global config", new Executable() {
            public void func_65815(Reactor session) throws Exception {
                loadConfig();
                                if (slaves != null && !slaves.isEmpty() && nodes.isLegacy()) {
                    nodes.setNodes(slaves);
                    slaves = null;
                } else {
                    nodes.load();
                }

                clouds.setOwner(Jenkins.this);
            }
        });

        for (final File subdir : subdirs) {
            g.requires(loadJenkins).attains(JOB_LOADED).notFatal().add("Loading item " + subdir.getName(), new Executable() {
                public void func_65815(Reactor session) throws Exception {
                    if(!Items.getConfigFile(subdir).exists()) {
                                                return;
                    }
                    TopLevelItem item = (TopLevelItem) Items.load(Jenkins.this, subdir);
                    items.put(item.getName(), item);
                    loadedNames.add(item.getName());
                }
            });
        }

        g.requires(JOB_LOADED).add("Cleaning up obsolete items deleted from the disk", new Executable() {
            public void func_65815(Reactor reactor) throws Exception {
                                                
                                                for (String name : items.keySet()) {
                    if (!loadedNames.contains(name))
                        items.remove(name);
                }
            }
        });

        g.requires(JOB_LOADED).add("Finalizing set up",new Executable() {
            public void func_65815(Reactor session) throws Exception {
                rebuildDependencyGraph();

                {                    for (Node slave : nodes.getNodes())
                                                slave.getAssignedLabels();
                    getAssignedLabels();
                }

                                                if(views.size()==0 || primaryView==null) {
                    View v = new AllView(AllView.DEFAULT_VIEW_NAME);
                    setViewOwner(v);
                    views.add(0,v);
                    primaryView = v.getViewName();
                }
                primaryView = AllView.migrateLegacyPrimaryAllViewLocalizedName(views, primaryView);

                if (useSecurity!=null && !useSecurity) {
                                                            authorizationStrategy = AuthorizationStrategy.UNSECURED;
                    setSecurityRealm(SecurityRealm.NO_AUTHENTICATION);
                } else {
                                        if(authorizationStrategy==null) {
                        if(useSecurity==null)
                            authorizationStrategy = AuthorizationStrategy.UNSECURED;
                        else
                            authorizationStrategy = new LegacyAuthorizationStrategy();
                    }
                    if(securityRealm==null) {
                        if(useSecurity==null)
                            setSecurityRealm(SecurityRealm.NO_AUTHENTICATION);
                        else
                            setSecurityRealm(new LegacySecurityRealm());
                    } else {
                                                setSecurityRealm(securityRealm);
                    }
                }


                                setCrumbIssuer(crumbIssuer);

                                for (Action a : getExtensionList(RootAction.class))
                    if (!actions.contains(a)) actions.add(a);
            }
        });

        return g;
    }