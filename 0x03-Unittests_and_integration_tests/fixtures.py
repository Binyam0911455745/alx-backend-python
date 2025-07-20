# fixtures.py

ORG_PAYLOAD = {
    "login": "google",
    "id": 1342004,
    "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
    "repos_url": "https://api.github.com/orgs/google/repos",
    "events_url": "https://api.github.com/orgs/google/events",
    "hooks_url": "https://api.github.com/orgs/google/hooks",
    "issues_url": "https://api.github.com/orgs/google/issues",
    "members_url": "https://api.github.com/orgs/google/members{/member}",
    "public_members_url": "https://api.github.com/orgs/google/" \
                          "public_members{/member}",
    "avatar_url": "https://avatars.githubusercontent.com/u/1342004?v=4",
    "description": "Google, home of the Android, Chrome, and many more!",
    "name": "Google",
    "company": None,
    "blog": "https://opensource.google/",
    "location": None,
    "email": None,
    "twitter_username": None,
    "is_verified": True,
    "has_organization_projects": True,
    "has_repository_projects": True,
    "public_repos": 1414,
    "public_gists": 0,
    "followers": 0,
    "following": 0,
    "html_url": "https://github.com/google",
    "created_at": "2012-01-25T20:12:12Z",
    "updated_at": "2024-07-16T15:23:44Z"
}

REPOS_PAYLOAD = [
    {
        "id": 13420040,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMzQyMDA0MA==",
        "name": "gocv",
        "full_name": "google/gocv",
        "private": False,
        "owner": {
            "login": "google",
            "id": 1342004,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
            "avatar_url": "https://avatars.githubusercontent.com/u/1342004?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/google",
            "html_url": "https://github.com/google",
            "followers_url": "https://api.github.com/users/google/followers",
            "following_url": "https://api.github.com/users/google/following{" \
                             "/other_user}",
            "gists_url": "https://api.github.com/users/google/gists{" \
                         "/gist_id}",
            "starred_url": "https://api.github.com/users/google/starred{" \
                           "/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/google/" \
                                 "subscriptions",
            "organizations_url": "https://api.github.com/users/google/" \
                                 "organizations",
            "repos_url": "https://api.github.com/users/google/repos",
            "events_url": "https://api.github.com/users/google/events{" \
                          "/privacy}",
            "received_events_url": "https://api.github.com/users/google/" \
                                   "received_events",
            "type": "Organization",
            "site_admin": False
        },
        "html_url": "https://github.com/google/gocv",
        "description": "GoCV: Go package for computer vision using OpenCV 4",
        "fork": False,
        "url": "https://api.github.com/repos/google/gocv",
        "forks_url": "https://api.github.com/repos/google/gocv/forks",
        "keys_url": "https://api.github.com/repos/google/gocv/keys{" \
                    "/key_id}",
        "collaborators_url": "https://api.github.com/repos/google/gocv/" \
                             "collaborators{/collaborator}",
        "teams_url": "https://api.github.com/repos/google/gocv/teams",
        "hooks_url": "https://api.github.com/repos/google/gocv/hooks",
        "issue_events_url": "https://api.github.com/repos/google/gocv/" \
                            "issues/events{/number}",
        "events_url": "https://api.github.com/repos/google/gocv/events",
        "assignees_url": "https://api.github.com/repos/google/gocv/" \
                         "assignees{/user}",
        "branches_url": "https://api.github.com/repos/google/gocv/" \
                        "branches{/branch}",
        "tags_url": "https://api.github.com/repos/google/gocv/tags",
        "blobs_url": "https://api.github.com/repos/google/gocv/git/blobs{" \
                     "/sha}",
        "git_tags_url": "https://api.github.com/repos/google/gocv/git/tags{" \
                        "/sha}",
        "git_refs_url": "https://api.github.com/repos/google/gocv/git/refs{" \
                        "/sha}",
        "trees_url": "https://api.github.com/repos/google/gocv/git/trees{" \
                     "/sha}",
        "statuses_url": "https://api.github.com/repos/google/gocv/statuses{" \
                        "sha}",
        "languages_url": "https://api.github.com/repos/google/gocv/" \
                         "languages",
        "stargazers_url": "https://api.github.com/repos/google/gocv/" \
                          "stargazers",
        "contributors_url": "https://api.github.com/repos/google/gocv/" \
                            "contributors",
        "subscribers_url": "https://api.github.com/repos/google/gocv/" \
                           "subscribers",
        "subscription_url": "https://api.github.com/repos/google/gocv/" \
                            "subscription",
        "commits_url": "https://api.github.com/repos/google/gocv/commits{" \
                       "/sha}",
        "git_commits_url": "https://api.github.com/repos/google/gocv/" \
                           "git/commits{/sha}",
        "comments_url": "https://api.github.com/repos/google/gocv/comments{" \
                        "/number}",
        "issue_comment_url": "https://api.github.com/repos/google/gocv/" \
                             "issues/comments{/number}",
        "contents_url": "https://api.github.com/repos/google/gocv/" \
                        "contents/{+path}",
        "compare_url": "https://api.github.com/repos/google/gocv/compare/" \
                       "{base}...{head}",
        "merges_url": "https://api.github.com/repos/google/gocv/merges",
        "archive_url": "https://api.github.com/repos/google/gocv/archive{" \
                       "archive_format}",
        "downloads_url": "https://api.github.com/repos/google/gocv/" \
                         "downloads",
        "issues_url": "https://api.github.com/repos/google/gocv/issues{" \
                      "/number}",
        "pulls_url": "https://api.github.com/repos/google/gocv/pulls{" \
                     "/number}",
        "milestones_url": "https://api.github.com/repos/google/gocv/" \
                           "milestones{/number}",
        "notifications_url": "https://api.github.com/repos/google/gocv/" \
                             "notifications{?since,all,participating}",
        "labels_url": "https://api.github.com/repos/google/gocv/labels{" \
                      "/name}",
        "releases_url": "https://api.github.com/repos/google/gocv/" \
                        "releases{/id}",
        "deployments_url": "https://api.github.com/repos/google/gocv/" \
                           "deployments",
        "created_at": "2013-10-09T03:08:48Z",
        "updated_at": "2024-07-16T09:42:32Z",
        "pushed_at": "2024-07-16T14:48:08Z",
        "git_url": "git://github.com/google/gocv.git",
        "ssh_url": "git@github.com:google/gocv.git",
        "clone_url": "https://github.com/google/gocv.git",
        "svn_url": "https://github.com/google/gocv",
        "homepage": "https://gocv.io/",
        "size": 55193,
        "stargazers_count": 5971,
        "watchers_count": 5971,
        "language": "Go",
        "has_issues": True,
        "has_projects": True,
        "has_downloads": True,
        "has_wiki": True,
        "has_pages": True,
        "has_discussions": False,
        "forks_count": 894,
        "mirror_url": None,
        "archived": False,
        "disabled": False,
        "open_issues_count": 142,
        "license": {"key": "apache-2.0", "name": "Apache License 2.0",
                    "spdx_id": "Apache-2.0",
                    "url": "https://api.github.com/licenses/apache-2.0",
                    "node_id": "MDc6TGljZW5zZTI="},
        "allow_forking": True,
        "is_template": False,
        "web_commit_signoff_required": False,
        "topics": ["go", "gocv", "golang", "opencv"],
        "visibility": "public",
        "forks": 894,
        "open_issues": 142,
        "watchers": 5971,
        "default_branch": "master",
        "temp_clone_token": None,
        "network_count": 894,
        "subscribers_count": 272
    },
    {
        "id": 13420041,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMzQyMDA0MQ==",
        "name": "guava",
        "full_name": "google/guava",
        "private": False,
        "owner": {
            "login": "google",
            "id": 1342004,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
            "avatar_url": "https://avatars.githubusercontent.com/u/1342004?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/google",
            "html_url": "https://github.com/google",
            "followers_url": "https://api.github.com/users/google/followers",
            "following_url": "https://api.github.com/users/google/following{" \
                             "/other_user}",
            "gists_url": "https://api.github.com/users/google/gists{" \
                         "/gist_id}",
            "starred_url": "https://api.github.com/users/google/starred{" \
                           "/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/google/" \
                                 "subscriptions",
            "organizations_url": "https://api.github.com/users/google/" \
                                 "organizations",
            "repos_url": "https://api.github.com/users/google/repos",
            "events_url": "https://api.github.com/users/google/events{" \
                          "/privacy}",
            "received_events_url": "https://api.github.com/users/google/" \
                                   "received_events",
            "type": "Organization",
            "site_admin": False
        },
        "html_url": "https://github.com/google/guava",
        "description": "Google core libraries for Java",
        "fork": False,
        "url": "https://api.github.com/repos/google/guava",
        "forks_url": "https://api.github.com/repos/google/guava/forks",
        "keys_url": "https://api.github.com/repos/google/guava/keys{" \
                    "/key_id}",
        "collaborators_url": "https://api.github.com/repos/google/guava/" \
                             "collaborators{/collaborator}",
        "teams_url": "https://api.github.com/repos/google/guava/teams",
        "hooks_url": "https://api.github.com/repos/google/guava/hooks",
        "issue_events_url": "https://api.github.com/repos/google/guava/" \
                            "issues/events{/number}",
        "events_url": "https://api.github.com/repos/google/guava/events",
        "assignees_url": "https://api.github.com/repos/google/guava/" \
                         "assignees{/user}",
        "branches_url": "https://api.github.com/repos/google/guava/" \
                        "branches{/branch}",
        "tags_url": "https://api.github.com/repos/google/guava/tags",
        "blobs_url": "https://api.github.com/repos/google/guava/git/blobs{" \
                     "/sha}",
        "git_tags_url": "https://api.github.com/repos/google/guava/git/tags{" \
                        "/sha}",
        "git_refs_url": "https://api.github.com/repos/google/guava/git/refs{" \
                        "/sha}",
        "trees_url": "https://api.github.com/repos/google/guava/git/trees{" \
                     "/sha}",
        "statuses_url": "https://api.github.com/repos/google/guava/statuses{" \
                        "sha}",
        "languages_url": "https://api.github.com/repos/google/guava/" \
                         "languages",
        "stargazers_url": "https://api.github.com/repos/google/guava/" \
                          "stargazers",
        "contributors_url": "https://api.github.com/repos/google/guava/" \
                            "contributors",
        "subscribers_url": "https://api.github.com/repos/google/guava/" \
                           "subscribers",
        "subscription_url": "https://api.github.com/repos/google/guava/" \
                            "subscription",
        "commits_url": "https://api.github.com/repos/google/guava/commits{" \
                       "/sha}",
        "git_commits_url": "https://api.github.com/repos/google/guava/" \
                           "git/commits{/sha}",
        "comments_url": "https://api.github.com/repos/google/guava/comments{" \
                        "/number}",
        "issue_comment_url": "https://api.github.com/repos/google/guava/" \
                             "issues/comments{/number}",
        "contents_url": "https://api.github.com/repos/google/guava/" \
                        "contents/{+path}",
        "compare_url": "https://api.github.com/repos/google/guava/compare/" \
                       "{base}...{head}",
        "merges_url": "https://api.github.com/repos/google/guava/merges",
        "archive_url": "https://api.github.com/repos/google/guava/archive{" \
                       "archive_format}",
        "downloads_url": "https://api.github.com/repos/google/guava/" \
                         "downloads",
        "issues_url": "https://api.github.com/repos/google/guava/issues{" \
                      "/number}",
        "pulls_url": "https://api.github.com/repos/google/guava/pulls{" \
                     "/number}",
        "milestones_url": "https://api.github.com/repos/google/guava/" \
                           "milestones{/number}",
        "notifications_url": "https://api.github.com/repos/google/guava/" \
                             "notifications{?since,all,participating}",
        "labels_url": "https://api.github.com/repos/google/guava/labels{" \
                      "/name}",
        "releases_url": "https://api.github.com/repos/google/guava/" \
                        "releases{/id}",
        "deployments_url": "https://api.github.com/repos/google/guava/" \
                           "deployments",
        "created_at": "2013-10-09T03:08:48Z",
        "updated_at": "2024-07-16T09:42:32Z",
        "pushed_at": "2024-07-16T14:48:08Z",
        "git_url": "git://github.com/google/guava.git",
        "ssh_url": "git@github.com:google/guava.git",
        "clone_url": "https://github.com/google/guava.git",
        "svn_url": "https://github.com/google/guava",
        "homepage": "https://github.com/google/guava",
        "size": 55193,
        "stargazers_count": 5971,
        "watchers_count": 5971,
        "language": "Java",
        "has_issues": True,
        "has_projects": True,
        "has_downloads": True,
        "has_wiki": True,
        "has_pages": True,
        "has_discussions": False,
        "forks_count": 894,
        "mirror_url": None,
        "archived": False,
        "disabled": False,
        "open_issues_count": 142,
        "license": {"key": "apache-2.0", "name": "Apache License 2.0",
                    "spdx_id": "Apache-2.0",
                    "url": "https://api.github.com/licenses/apache-2.0",
                    "node_id": "MDc6TGljZW5zZTI="},
        "allow_forking": True,
        "is_template": False,
        "web_commit_signoff_required": False,
        "topics": ["java"],
        "visibility": "public",
        "forks": 894,
        "open_issues": 142,
        "watchers": 5971,
        "default_branch": "master",
        "temp_clone_token": None,
        "network_count": 894,
        "subscribers_count": 272
    },
    {
        "id": 13420042,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMzQyMDA0Mg==",
        "name": "closure-compiler",
        "full_name": "google/closure-compiler",
        "private": False,
        "owner": {
            "login": "google",
            "id": 1342004,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
            "avatar_url": "https://avatars.githubusercontent.com/u/1342004?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/google",
            "html_url": "https://github.com/google",
            "followers_url": "https://api.github.com/users/google/followers",
            "following_url": "https://api.github.com/users/google/following{" \
                             "/other_user}",
            "gists_url": "https://api.github.com/users/google/gists{" \
                         "/gist_id}",
            "starred_url": "https://api.github.com/users/google/starred{" \
                           "/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/google/" \
                                 "subscriptions",
            "organizations_url": "https://api.github.com/users/google/" \
                                 "organizations",
            "repos_url": "https://api.github.com/users/google/repos",
            "events_url": "https://api.github.com/users/google/events{" \
                          "/privacy}",
            "received_events_url": "https://api.github.com/users/google/" \
                                   "received_events",
            "type": "Organization",
            "site_admin": False
        },
        "html_url": "https://github.com/google/closure-compiler",
        "description": "A JavaScript optimizing compiler.",
        "fork": False,
        "url": "https://api.github.com/repos/google/closure-compiler",
        "forks_url": "https://api.github.com/repos/google/closure-compiler/" \
                     "forks",
        "keys_url": "https://api.github.com/repos/google/closure-compiler/" \
                    "keys{/key_id}",
        "collaborators_url": "https://api.github.com/repos/google/" \
                             "closure-compiler/collaborators{/collaborator}",
        "teams_url": "https://api.github.com/repos/google/" \
                     "closure-compiler/teams",
        "hooks_url": "https://api.github.com/repos/google/" \
                     "closure-compiler/hooks",
        "issue_events_url": "https://api.github.com/repos/google/" \
                            "closure-compiler/issues/events{/number}",
        "events_url": "https://api.github.com/repos/google/" \
                      "closure-compiler/events",
        "assignees_url": "https://api.github.com/repos/google/" \
                         "closure-compiler/assignees{/user}",
        "branches_url": "https://api.github.com/repos/google/" \
                        "closure-compiler/branches{/branch}",
        "tags_url": "https://api.github.com/repos/google/" \
                    "closure-compiler/tags",
        "blobs_url": "https://api.github.com/repos/google/" \
                     "closure-compiler/git/blobs{" \
                     "/sha}",
        "git_tags_url": "https://api.github.com/repos/google/" \
                        "closure-compiler/git/tags{" \
                        "/sha}",
        "git_refs_url": "https://api.github.com/repos/google/" \
                        "closure-compiler/git/refs{" \
                        "/sha}",
        "trees_url": "https://api.github.com/repos/google/" \
                     "closure-compiler/git/trees{" \
                     "/sha}",
        "statuses_url": "https://api.github.com/repos/google/" \
                        "closure-compiler/statuses/{sha}",
        "languages_url": "https://api.github.com/repos/google/" \
                         "closure-compiler/languages",
        "stargazers_url": "https://api.github.com/repos/google/" \
                          "closure-compiler/stargazers",
        "contributors_url": "https://api.github.com/repos/google/" \
                            "closure-compiler/contributors",
        "subscribers_url": "https://api.github.com/repos/google/" \
                           "closure-compiler/subscribers",
        "subscription_url": "https://api.github.com/repos/google/" \
                            "closure-compiler/subscription",
        "commits_url": "https://api.github.com/repos/google/" \
                       "closure-compiler/commits{" \
                       "/sha}",
        "git_commits_url": "https://api.github.com/repos/google/" \
                           "closure-compiler/git/commits{" \
                           "/sha}",
        "comments_url": "https://api.github.com/repos/google/" \
                        "closure-compiler/comments{" \
                        "/number}",
        "issue_comment_url": "https://api.github.com/repos/google/" \
                             "closure-compiler/issues/comments{/number}",
        "contents_url": "https://api.github.com/repos/google/" \
                        "closure-compiler/contents/{+path}",
        "compare_url": "https://api.github.com/repos/google/" \
                       "closure-compiler/compare/{base}...{head}",
        "merges_url": "https://api.github.com/repos/google/" \
                      "closure-compiler/merges",
        "archive_url": "https://api.github.com/repos/google/" \
                       "closure-compiler/archive/{archive_format}",
        "downloads_url": "https://api.github.com/repos/google/" \
                         "closure-compiler/downloads",
        "issues_url": "https://api.github.com/repos/google/" \
                      "closure-compiler/issues{" \
                      "/number}",
        "pulls_url": "https://api.github.com/repos/google/" \
                     "closure-compiler/pulls{" \
                     "/number}",
        "milestones_url": "https://api.github.com/repos/google/" \
                           "closure-compiler/milestones{" \
                           "/number}",
        "notifications_url": "https://api.github.com/repos/google/" \
                             "closure-compiler/notifications{?since,all," \
                             "participating}",
        "labels_url": "https://api.github.com/repos/google/" \
                      "closure-compiler/labels{" \
                      "/name}",
        "releases_url": "https://api.github.com/repos/google/" \
                        "closure-compiler/releases{" \
                        "/id}",
        "deployments_url": "https://api.github.com/repos/google/" \
                           "closure-compiler/deployments",
        "created_at": "2013-10-09T03:08:48Z",
        "updated_at": "2024-07-16T09:42:32Z",
        "pushed_at": "2024-07-16T14:48:08Z",
        "git_url": "git://github.com/google/closure-compiler.git",
        "ssh_url": "git@github.com:google/closure-compiler.git",
        "clone_url": "https://github.com/google/closure-compiler.git",
        "svn_url": "https://github.com/google/closure-compiler",
        "homepage": "https://developers.google.com/closure/compiler",
        "size": 55193,
        "stargazers_count": 5971,
        "watchers_count": 5971,
        "language": "Java",
        "has_issues": True,
        "has_projects": True,
        "has_downloads": True,
        "has_wiki": True,
        "has_pages": True,
        "has_discussions": False,
        "forks_count": 894,
        "mirror_url": None,
        "archived": False,
        "disabled": False,
        "open_issues_count": 142,
        "license": {"key": "other", "name": "Other License"}, # No apache-2.0
        "allow_forking": True,
        "is_template": False,
        "web_commit_signoff_required": False,
        "topics": ["javascript", "compiler"],
        "visibility": "public",
        "forks": 894,
        "open_issues": 142,
        "watchers": 5971,
        "default_branch": "master",
        "temp_clone_token": None,
        "network_count": 894,
        "subscribers_count": 272
    }
]

EXPECTED_REPOS = ["gocv", "guava", "closure-compiler"]

APACHE2_REPOS = ["gocv", "guava"]