#include <iostream>
using namespace std;

class Node {
public:
    // To store the Value or data
    int data;

    // Pointer to point the Previous Element
    Node* prev;

    // Pointer to point the Next Element
    Node* next;

    // Constructor
    Node(int d) {
        data = d;
        prev = nullptr;
        next = nullptr;
    }
};

void print(Node* head) {
    Node* temp = head;      
    while (temp != nullptr) {
        cout << temp->data << " ";  
        temp = temp->next;
    }
    cout << endl;
}

int main(){
    Node* first = new Node(10);
    Node* second = new Node(20);
    Node* third = new Node(30);
    
    // Linking the Nodes
    first->next = second;
    second->prev = first;
    second->next = third;
    third->prev = second;

    print(first);

    // Freeing the allocated memory
    delete first;
    delete second;
    delete third;
}