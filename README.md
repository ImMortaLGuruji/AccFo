# AccFo
AccFo provides a secure and convenient solution for storing and managing account information. It offers features for adding, generating, removing, and viewing data, ensuring that users can securely store their sensitive information. With strong encryption techniques and the requirement of a master password for decryption, AccFo provides a reliable way to protect user data.

# Key Features:
## Adding Data:
AccFo allows users to add their account information, including the username and password, to the secure storage. When adding data, the user provides the necessary details, and the app encrypts the information before storing it in the SQL database.

## Generating Password:
AccFo also includes a password generator feature that allows users to generate strong and secure passwords. The user can specify the desired length of the password, and the app generates a random password using secure algorithms. This feature helps users create unique and robust passwords for their accounts.

## Removing Data:
Users can remove any stored account information from AccFo's database. This feature enables users to delete outdated or unnecessary account entries securely. Upon deletion, the app ensures that the removed data is permanently deleted and cannot be recovered.

## Viewing Data:
AccFo provides a feature to view the stored account information in a secure manner. Users can access their stored data by providing the master password. The app then decrypts and displays the relevant account details. This feature ensures that users can conveniently retrieve their account information whenever needed.

## Multiple Accounts:
AccFo goes beyond simple account storage and offers a powerful feature that allows users to create and segregate multiple accounts based on their use cases. This functionality enables users to organize their account information more effectively and maintain a structured approach to managing their various online activities.

## Encryption and Security:
AccFo employs strong encryption techniques to protect the stored data. It utilizes encryption algorithms such as AES (Advanced Encryption Standard) to encrypt the account information before storing it in the SQL database. These encryption algorithms ensure that the data remains secure even if the database is compromised.

The master password plays a crucial role in the decryption process. Without the master password, the encrypted data cannot be decrypted, providing an additional layer of security. It is essential for users to create a strong and unique master password to prevent unauthorized access to their account information.

## Database:
AccFo employs SQL (Structured Query Language) as the backend database management system to store the encrypted account information. SQL databases are widely used and offer robust data management capabilities. The app uses SQL queries to insert, retrieve, update, and delete the encrypted data from the database. The data is stored locally on your device.
