# Asian Society Health and Exercise website

This repository contains the source code for the ASHE Research Paper Management System. ASHE (Asian Society Health and Exercise) is a scholarly society that publishes research papers (theses or dissertations) related to human health and exercise. The web application allows users to login, signup, and submit their doctorate-level research papers for review and publication. The admin user manages the submission process, assigns reviewers, and decides which papers to publish. All user credentials, papers, and related information (title, author, context, files) are stored in Firebase.

## Table of Contents

- Introduction
- Features
- Usage
- Dependencies


## Introduction

The ASHE Research Paper Management System is a web application developed using Flask, a micro web framework for Python. The system provides a platform for ASHE members to submit their research papers, which are then reviewed and published by the society. It leverages Firebase for user authentication, storage of papers and associated files, and database management.

## Features

- User authentication: Users can sign up and log in to access the system.
- Paper submission: Regular members can submit their research papers for review and publication.
- Paper review process: The admin user assigns reviewers to papers and decides whether to publish them.
- Paper publication: Admin users can publish accepted papers for all members to read and download.
- Front page customization: Admin users can upload an image to be displayed on the front page.

## Usage

1. Upon launching the application, users will be directed to the homepage, where they can log in or sign up.

2. After logging in, regular members can submit their research papers by filling out the necessary details and uploading the files.

3. Admin users can view the list of submitted papers and assign reviewers to each paper.

4. Admin users can review the assigned papers and decide whether to publish them or reject them.

5. Published papers will be accessible to all members, who can read and download them from the system.

6. Admin users can also customize the front page by uploading an image to be displayed.


## Dependencies

The ASHE Research Paper Management System relies on the following libraries and services:

- Flask: A micro web framework for Python.
- Firebase: A platform for building web and mobile applications.
- pdf2image: A library for converting PDF files to images.
