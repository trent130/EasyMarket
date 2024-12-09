'use client';

import React from 'react';
import type { ProductSearchFilters, Category, ProductCondition } from '../../types/product';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Checkbox } from '../ui/checkbox';

interface ProductFilterProps {
    filters?: Partial<ProductSearchFilters>; // Make filters optional
    categories: Category[];
    onChange: (filters: Partial<ProductSearchFilters>) => void;
}

export default function ProductFilter({ 
    filters = {}, // Provide a default empty object
    categories = [], // Provide a default empty array 
    onChange 
}: ProductFilterProps) {
    const conditions = [
        { value: 'new', label: 'New' },
        { value: 'like_new', label: 'Like New' },
        { value: 'good', label: 'Good' },
        { value: 'fair', label: 'Fair' },
    ];

    const handleConditionChange = (value: ProductCondition) => {
        // This function updates the condition in the filters
        onChange({ condition: value });
    };


    return (
        <div className="space-y-6">
            {/* Price Range */}
            <div className="space-y-2">
                <Label>Price Range</Label>
                <div className="flex items-center gap-2">
                    <Input
                        type="number"
                        placeholder="Min"
                        value={filters.min_price ?? ''} // Use nullish coalescing
                        onChange={(e) => onChange({ 
                            min_price: e.target.value 
                                ? Number(e.target.value) 
                                : undefined 
                        })}
                        className="w-24"
                    />
                    <span>to</span>
                    <Input
                        type="number"
                        placeholder="Max"
                        value={filters.max_price ?? ''} // Use nullish coalescing
                        onChange={(e) => onChange({ 
                            max_price: e.target.value 
                                ? Number(e.target.value) 
                                : undefined 
                        })}
                        className="w-24"
                    />
                </div>
            </div>

            {/* Categories */}
            <div className="space-y-2">
                <Label>Categories</Label>
                <div className="grid grid-cols-2 gap-2">
                    {categories.map((category) => (
                        <Button
                            key={category.id}
                            variant={filters.category === category.id ? 'default' : 'outline'}
                            onClick={() => onChange({ category: category.id })}
                            className="justify-start"
                        >
                            {category.name}
                            {category.product_count > 0 && (
                                <span className="ml-auto text-xs text-muted-foreground">
                                    ({category.product_count})
                                </span>
                            )}
                        </Button>
                    ))}
                </div>
            </div>

            {/* Condition */}
            <div className="space-y-2">
                <Label>Condition</Label>
                <RadioGroup
                    value={filters.condition || ''}
                    onValueChange={handleConditionChange}
                >
                    {conditions.map((condition) => (
                        <div key={condition.value} className="flex items-center space-x-2">
                            <RadioGroupItem value={condition.value} id={condition.value} />
                            <Label htmlFor={condition.value}>{condition.label}</Label>
                        </div>
                    ))}
                </RadioGroup>
            </div>

            {/* Stock Status */}
            <div className="flex items-center space-x-2">
                <Checkbox
                    id="in_stock"
                    checked={filters.in_stock}
                    onCheckedChange={(checked) => onChange({ in_stock: checked as boolean })}
                />
                <Label htmlFor="in_stock">In Stock Only</Label>
            </div>

            {/* Clear Filters */}
            <Button
                variant="outline"
                className="w-full"
                onClick={() => onChange({
                    category: undefined,
                    min_price: undefined,
                    max_price: undefined,
                    condition: undefined,
                    in_stock: undefined,
                })}
            >
                Clear Filters
            </Button>
        </div>
    );
}
